// アプリの動きの測定用（2026-10-04、本人「使用感・ラグ・バグの調査」）。
// パソコンの Edge を画面なし（headless）で動かし、実際に描画させながら、画面ごとの速さ・引っかかりを測る。
// 使い方（先に npm run build と npm run preview -- --port 4173、実データの ZIP を配る CORS つきの簡単なサーバー 8765 を起動）：
//   node tools/perf/cdp.mjs seed     … 空の測定用プロファイルに、実データ（枠 6,142・画像 6,091）を入れる（1 回だけ。約 2 分）
//   node tools/perf/cdp.mjs measure  … 画面ごとの速さを測る（CPU を 4 倍遅くして、iPhone に近づける。CPU=1 で等速）
import { spawn } from 'node:child_process'
import { mkdirSync, rmSync } from 'node:fs'

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
const PROFILE = process.env.PROFILE ?? 'C:/Users/kazuk/AppData/Local/Temp/pocamaster-perf-profile'
const PORT = 9333
const APP = process.env.APP ?? 'http://localhost:4173/pocamaster/'
const CPU = Number(process.env.CPU ?? 4)
const mode = process.argv[2] ?? 'measure'

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function launch() {
  mkdirSync(PROFILE, { recursive: true })
  const p = spawn(EDGE, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`, '--headless=new', '--no-first-run', '--no-default-browser-check', '--window-size=390,844', 'about:blank'], { stdio: 'ignore' })
  for (let i = 0; i < 60; i++) {
    try {
      const t = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()
      const page = t.find((x) => x.type === 'page')
      if (page) return { proc: p, ws: page.webSocketDebuggerUrl }
    } catch { /* まだ */ }
    await sleep(250)
  }
  throw new Error('Edge が起動しません')
}

function connect(url) {
  const ws = new WebSocket(url)
  let id = 0
  const waiting = new Map()
  const events = []
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data)
    if (d.id && waiting.has(d.id)) {
      const { res, rej } = waiting.get(d.id)
      waiting.delete(d.id)
      d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result)
    } else if (d.method) events.push(d)
  }
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; waiting.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })) })
  const ready = new Promise((r) => (ws.onopen = r))
  const ev = async (expr, awaitPromise = true) => {
    const r = await send('Runtime.evaluate', { expression: expr, awaitPromise, returnByValue: true })
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? JSON.stringify(r.exceptionDetails))
    return r.result.value
  }
  return { ready, send, ev, events, close: () => ws.close() }
}

// ページの中で使う測定の道具（毎回の読み込みのあとに入れる）
const HARNESS = `(() => {
  if (window.__h) return;
  const h = window.__h = { lt: [] };
  new PerformanceObserver((l) => l.getEntries().forEach((e) => h.lt.push(Math.round(e.duration)))).observe({ type: 'longtask', buffered: true });
  // 次の n 回の描画が終わるまで（rAF の 2 回目は、前の描画が画面に出たあと）
  h.frames = (n = 2) => new Promise((res) => { let k = 0; const f = () => (++k >= n ? res(performance.now()) : requestAnimationFrame(f)); requestAnimationFrame(f); });
  // 描画が落ち着く（DOM の変化が quiet ms 止まる）まで
  h.settle = (quiet = 350, max = 15000) => new Promise((res) => {
    const t0 = performance.now(); let last = t0;
    const mo = new MutationObserver(() => { last = performance.now(); });
    mo.observe(document.body, { subtree: true, childList: true, attributes: true });
    const iv = setInterval(() => { const now = performance.now(); if (now - last >= quiet || now - t0 > max) { clearInterval(iv); mo.disconnect(); res(Math.round(last - t0)); } }, 30);
  });
  h.run = async (label, action, opts = {}) => {
    const lt0 = h.lt.length; const t0 = performance.now();
    await action();
    const tFrame = Math.round((await h.frames(2)) - t0);   // 操作から、描画が画面に出るまで
    const tSettle = await h.settle(opts.quiet);             // 描画が落ち着くまで（画像の読み込みを含む）
    const lts = h.lt.slice(lt0);
    return { label, 画面に出るまで_ms: tFrame, 落ち着くまで_ms: Math.round(tFrame + tSettle), 長い処理: lts.length, 最長_ms: Math.max(0, ...lts), 合計_ms: lts.reduce((a, b) => a + b, 0), img: document.images.length, 読み込み済みimg: [...document.images].filter((i) => i.complete && i.naturalWidth).length, DOM: document.getElementsByTagName('*').length };
  };
  // スクロールのなめらかさ：一定の速さで下へ動かし、描画の間隔を測る
  h.scroll = (px, ms) => new Promise((res) => {
    const start = scrollY, t0 = performance.now(); let prev = t0; const gaps = [];
    const f = (now) => { gaps.push(now - prev); prev = now; const p = Math.min(1, (now - t0) / ms); scrollTo(0, start + px * p); p < 1 ? requestAnimationFrame(f) : res(gaps); };
    requestAnimationFrame(f);
  }).then((g) => ({ frames: g.length, 平均_ms: Math.round(g.reduce((a, b) => a + b, 0) / g.length), 遅い描画_33ms超: g.filter((x) => x > 33).length, 最大_ms: Math.round(Math.max(...g)) }));
})()`

// 保存版（サービスワーカーとキャッシュ）を消す：消さないと、前に取り込んだ古いコードのまま測ってしまう（IndexedDB のデータは消さない）
async function clearSW(c) {
  await c.send('Storage.clearDataForOrigin', { origin: new URL(APP).origin, storageTypes: 'service_workers,cache_storage' })
}

async function open(devices = true) {
  const { proc, ws } = await launch()
  const c = connect(ws)
  await c.ready
  await c.send('Page.enable')
  await c.send('Runtime.enable')
  await c.send('Performance.enable')
  if (devices) {
    await c.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 3, mobile: true })
    await c.send('Emulation.setTouchEmulationEnabled', { enabled: true })
  }
  return { proc, c }
}

async function load(c, url) {
  await c.send('Page.navigate', { url })
  await sleep(500)
  for (let i = 0; i < 80; i++) {
    if (await c.ev('document.readyState').catch(() => '') === 'complete') break
    await sleep(100)
  }
  await c.ev(HARNESS)
}

const metrics = async (c) => Object.fromEntries((await c.send('Performance.getMetrics')).metrics.filter((m) => ['JSHeapUsedSize', 'LayoutCount', 'RecalcStyleCount', 'Nodes'].includes(m.name)).map((m) => [m.name, m.value]))

async function seed() {
  rmSync(PROFILE, { recursive: true, force: true })
  const { proc, c } = await open(false)
  await load(c, APP + '#/settings')
  await sleep(1500)
  console.log('初期データを取り込む…')
  await c.ev(`(async () => { [...document.querySelectorAll('button')].find(b => b.innerText.includes('初期データを取り込む')).click(); for (let i = 0; i < 60; i++) { await new Promise(r => setTimeout(r, 500)); if (document.querySelector('[role=status]')?.innerText.includes('追加しました')) return; } })()`)
  console.log('画像の ZIP を取り込む…（約 2 分）')
  await c.ev(`(async () => { const blob = await fetch('http://127.0.0.1:8765/pocamaster-images.zip').then(r => r.blob()); const btn = [...document.querySelectorAll('button')].find(b => b.innerText.includes('画像をまとめて取り込む')); const dt = new DataTransfer(); dt.items.add(new File([blob], 'pocamaster-images.zip')); btn.nextElementSibling.files = dt.files; btn.nextElementSibling.dispatchEvent(new Event('change', { bubbles: true })); })()`)
  for (let i = 0; i < 400; i++) {
    const s = await c.ev(`document.querySelector('[role=status]')?.innerText ?? ''`)
    if (s.includes('取り込みました') || s.includes('失敗')) { console.log(s); break }
    await sleep(1000)
  }
  // 持っているカード（4 枚に 1 枚）とお気に入りを、実際の使い方に近づけるために付ける
  await c.ev(`new Promise((res, rej) => { const r = indexedDB.open('pocamaster'); r.onsuccess = () => { const db = r.result; const tx = db.transaction(['cards','statusHistory'], 'readwrite'); const st = tx.objectStore('cards'); const hi = tx.objectStore('statusHistory'); const q = st.getAll(); q.onsuccess = () => { q.result.forEach((c, i) => { if (i % 4 === 0) { c.status = '所持中'; c.statusChangedAt = Date.now() - i * 60000; if (i % 40 === 0) c.favorite = true; st.put(c); hi.add({ cardId: c.id, from: '未所持', to: '所持中', changedAt: c.statusChangedAt }); } }); }; tx.oncomplete = () => { db.close(); res(1); }; tx.onerror = rej; }; })`)
  console.log('済み')
  c.close(); proc.kill()
}

async function measure() {
  const { proc, c } = await open(true)
  await c.send('Emulation.setCPUThrottlingRate', { rate: CPU })
  await clearSW(c)
  const out = []
  // 1) アプリを開いたとき（起動）
  const t0 = Date.now()
  await c.send('Page.navigate', { url: APP + '#/' })
  await sleep(300)
  for (let i = 0; i < 100; i++) { if (await c.ev(`document.readyState`).catch(() => '') === 'complete') break; await sleep(50) }
  await c.ev(HARNESS)
  // 実験用：持っていないカードを暗くする filter を外した場合（NOFILTER=1）／別の見せ方（EXTRA_CSS）
  if (process.env.NOFILTER) await c.ev(`document.head.insertAdjacentHTML('beforeend', '<style>.poca.off{filter:none!important}</style>')`)
  if (process.env.EXTRA_CSS) await c.ev(`document.head.insertAdjacentHTML('beforeend', ${JSON.stringify('<style>' + process.env.EXTRA_CSS + '</style>')})`)
  const firstUi = await c.ev(`new Promise((res) => { const t0 = performance.now(); const iv = setInterval(() => { if (document.querySelector('.section-title, .banner, .empty')) { clearInterval(iv); res(Math.round(performance.now())); } }, 20); setTimeout(() => res(-1), 20000); })`)
  const st = await c.ev(`window.__h.settle(500)`)
  out.push({ label: '起動：アプリを開いてホームが出るまで', 内容が出る_ms: firstUi, 落ち着くまで_ms: firstUi + st, 長い処理: (await c.ev('window.__h.lt.length')), 合計_ms: (await c.ev('window.__h.lt.reduce((a,b)=>a+b,0)')), DOM: await c.ev('document.getElementsByTagName("*").length') })
  const ids = await c.ev(`(async () => { const cols = await new Promise((res) => { const r = indexedDB.open('pocamaster'); r.onsuccess = () => { const q = r.result.transaction('collections').objectStore('collections').getAll(); q.onsuccess = () => { res(q.result); r.result.close(); }; }; }); const f = (n) => cols.find((c) => c.name === n).id; return { secret: f('IVE SECRET'), revive: f('REVIVE+'), small: cols.find((c) => c.name.includes('ELEVEN')).id }; })()`)
  const go = (label, hash, quiet) => c.ev(`window.__h.run(${JSON.stringify(label)}, () => { location.hash = ${JSON.stringify(hash)} }, { quiet: ${quiet ?? 350} })`)
  out.push(await go('画面：コレクション一覧', '#/collections'))
  out.push(await go('画面：コレクション（IVE SECRET・563 枠）', '#/collections/' + ids.secret))
  out.push({ label: 'スクロール：IVE SECRET を上から下まで（約 18,000px を 4 秒）', ...(await c.ev(`window.__h.scroll(15000, 4000)`)) })
  out.push(await c.ev(`window.__h.run('スクロールのあと、画像が落ち着くまで', async () => {})`))
  await c.ev(`scrollTo(0, 0)`)
  out.push(await go('画面：ホーム（戻る）', '#/'))
  out.push(await go('画面：コレクション（REVIVE+・552 枠）', '#/collections/' + ids.revive))
  out.push(await go('画面：コレクション（小さい）', '#/collections/' + ids.small))
  out.push(await go('画面：マイアルバム', '#/albums'))
  out.push(await go('画面：カードを探す', '#/search'))
  out.push(await go('画面：求・譲', '#/wants'))
  out.push(await go('画面：集めた記録', '#/history'))
  out.push(await go('画面：設定', '#/settings'))
  // 2) 操作
  await go('(準備)', '#/collections/' + ids.secret)
  await sleep(1500)
  out.push(await c.ev(`window.__h.run('操作：カードを 1 枚タップ（持っている⇄持っていない）', () => { document.querySelectorAll('.poca')[5].click() })`))
  out.push(await c.ev(`window.__h.run('操作：同じカードをもう一度タップ', () => { document.querySelectorAll('.poca')[5].click() })`))
  out.push(await c.ev(`window.__h.run('操作：メンバーを切り替え（ユジン）', () => { [...document.querySelectorAll('.chip')].find(b => b.innerText.includes('ユジン')).click() })`))
  out.push(await c.ev(`window.__h.run('操作：「所持中」だけに絞り込み', () => { [...document.querySelectorAll('.chip')].find(b => b.innerText.includes('所持中')).click() })`))
  out.push(await c.ev(`window.__h.run('操作：絞り込みを「すべて」へ', () => { [...document.querySelectorAll('.chip')].filter(b => b.innerText.trim() === 'すべて').forEach(b => b.click()) })`))
  await go('(準備)', '#/')
  await sleep(1500)
  out.push(await c.ev(`window.__h.run('操作：ホームでメンバーを切り替え（ガウル）', () => { [...document.querySelectorAll('.chip')].find(b => b.innerText.includes('ガウル')).click() })`))
  out.push(await c.ev(`window.__h.run('操作：ホームでメンバーを切り替え（すべて）', () => { [...document.querySelectorAll('.chip')].find(b => b.innerText.trim() === 'すべて').click() })`))
  await go('(準備)', '#/search')
  await sleep(800)
  for (const q of ['K', 'KM', 'KMON', 'KMONSTAR']) {
    out.push(await c.ev(`window.__h.run('操作：検索に「${q}」と入力', () => { const i = document.querySelector('input[type=search], input'); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; set.call(i, ${JSON.stringify(q)}); i.dispatchEvent(new Event('input', { bubbles: true })) })`))
  }
  const m = await metrics(c)
  console.log(JSON.stringify({ CPU遅延: CPU + '倍', 全体: m, 結果: out }, null, 1))
  c.close(); proc.kill()
}

// 関数ごとの時間（CPU プロファイル）。圧縮なしの版（vite build --minify false --outDir dist-prof → preview 4174）で使うと、関数名が読める
function report(label, profile) {
  const nodes = new Map(profile.nodes.map((n) => [n.id, n]))
  const self = new Map()
  profile.samples.forEach((id, i) => self.set(id, (self.get(id) ?? 0) + profile.timeDeltas[i]))
  const agg = new Map()
  let total = 0
  for (const [id, t] of self) {
    const n = nodes.get(id)
    total += t
    const k = `${n.callFrame.functionName || '(無名)'}  ${n.callFrame.url.split('/').pop().split('?')[0]}:${n.callFrame.lineNumber + 1}`
    agg.set(k, (agg.get(k) ?? 0) + t)
  }
  const idle = [...agg].filter(([k]) => /^\((idle|program)\)/.test(k)).reduce((a, [, t]) => a + t, 0)
  console.log(`
■ ${label}（処理の合計 ${Math.round((total - idle) / 1000)}ms）`)
  ;[...agg].filter(([k]) => !/^\((idle|program)\)/.test(k)).sort((a, b) => b[1] - a[1]).slice(0, 14).forEach(([k, t]) => console.log(`  ${String(Math.round(t / 1000)).padStart(5)}ms  ${k}`))
}

async function profile() {
  const { proc, c } = await open(true)
  await c.send('Emulation.setCPUThrottlingRate', { rate: CPU })
  await clearSW(c)
  await c.send('Profiler.enable')
  await c.send('Profiler.setSamplingInterval', { interval: 400 })
  const prof = async (label, fn) => {
    await c.send('Profiler.start')
    await fn()
    report(label, (await c.send('Profiler.stop')).profile)
  }
  const ids = async () => c.ev(`(async () => { const cols = await new Promise((res) => { const r = indexedDB.open('pocamaster'); r.onsuccess = () => { const q = r.result.transaction('collections').objectStore('collections').getAll(); q.onsuccess = () => { res(q.result); r.result.close(); }; }; }); return { secret: cols.find((c) => c.name === 'IVE SECRET').id }; })()`)
  await prof('起動（アプリを開いてホームが落ち着くまで）', async () => {
    await c.send('Page.navigate', { url: APP + '#/' })
    await sleep(300)
    for (let i = 0; i < 200; i++) { if ((await c.ev(`document.readyState`).catch(() => '')) === 'complete') break; await sleep(50) }
    await c.ev(HARNESS)
    await c.ev(`new Promise((res) => { const iv = setInterval(() => { if (document.querySelector('.section-title, .banner, .empty')) { clearInterval(iv); res(1) } }, 30) })`)
    await c.ev(`window.__h.settle(600)`)
  })
  const { secret } = await ids()
  await prof('コレクション一覧を開く', () => c.ev(`window.__h.run('x', () => { location.hash = '#/collections' }, { quiet: 600 })`))
  await prof('IVE SECRET を開く', () => c.ev(`window.__h.run('x', () => { location.hash = '#/collections/${secret}' }, { quiet: 600 })`))
  await prof('IVE SECRET をスクロール（約 15,000px を 4 秒）', async () => { await c.ev(`window.__h.scroll(15000, 4000)`); await c.ev(`window.__h.settle(600)`) })
  await c.ev(`window.__h.run('x', () => { location.hash = '#/' }, { quiet: 800 })`)
  await sleep(1000)
  await c.ev(`[...document.querySelectorAll('.chip')].find(b => b.innerText.includes('ガウル')).click()`)
  await sleep(1500)
  await prof('ホームでメンバー「ガウル」→「すべて」', () => c.ev(`window.__h.run('x', () => { [...document.querySelectorAll('.chip')].find(b => b.innerText.trim() === 'すべて').click() }, { quiet: 600 })`))
  c.close(); proc.kill()
}

// 2 回目以降の起動（実際のアプリ：保存版から起動）。1 回目で保存版を入れ、そのあと k 回開き直して、ホームが出るまでと処理の合計を測る
async function startup() {
  const { proc, c } = await open(true)
  await c.send('Emulation.setCPUThrottlingRate', { rate: CPU })
  await clearSW(c)
  await load(c, APP + '#/')
  await sleep(5000) // 保存版（サービスワーカー）が入るのを待つ
  const k = Number(process.env.K ?? 3)
  const res = []
  for (let i = 0; i < k; i++) {
    await c.send('Page.navigate', { url: 'about:blank' })
    await sleep(500)
    await c.send('Page.navigate', { url: APP + '#/' })
    await sleep(300)
    for (let j = 0; j < 200; j++) { if ((await c.ev(`document.readyState`).catch(() => '')) === 'complete') break; await sleep(30) }
    await c.ev(HARNESS)
    const first = await c.ev(`new Promise((res) => { const iv = setInterval(() => { if (document.querySelector('.section-title, .banner, .empty')) { clearInterval(iv); res(Math.round(performance.now())); } }, 15); setTimeout(() => res(-1), 20000); })`)
    const st = await c.ev(`window.__h.settle(500)`)
    res.push({ 内容が出る_ms: first, 落ち着く_ms: first + st, 処理合計_ms: await c.ev('window.__h.lt.reduce((a,b)=>a+b,0)'), 長い処理: await c.ev('window.__h.lt.length'), 最長_ms: await c.ev('Math.max(0, ...window.__h.lt)') })
  }
  console.log(JSON.stringify(res))
  c.close(); proc.kill()
}

try {
  await (mode === 'seed' ? seed() : mode === 'profile' ? profile() : mode === 'startup' ? startup() : measure())
  process.exit(0)
} catch (e) {
  console.error('失敗：', e.message)
  process.exit(1)
}
