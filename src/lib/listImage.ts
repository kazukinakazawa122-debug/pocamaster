import { getFull, getThumb, type Card } from './db'
import { MEMBER_BY_ID, MEMBERS, memberLabel, memberNames, memberOrder } from './members'

/**
 * 「求」「譲」の一覧を画像にする（本人の要望、2026-10-01：X などに載せやすい 1 枚の画像）。
 * 見せる相手の画面に合わせ、いつも明るい色（紙の白・インクの黒）で描く。
 * iPhone では大きすぎる画像を作れないので、高さが MAX_H を超えたら何枚かに分ける
 */

const W = 1080
const PAD = 40
const MAX_H = 7600
const BG = '#f4f4f2'
const INK = '#1f1f1f'
const MUTED = '#6b6b68'
const FONT = '-apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif'

export interface ListImageGroup {
  name: string
  cards: Card[]
}

export interface ListImageOptions {
  /** 見出しの印（「求」か「譲」） */
  mark: string
  /** 見出しの文字（メンバー名・コレクション名） */
  title: string
  groups: ListImageGroup[]
  columns: number
  labels: boolean
  /** ファイルの名前に使う（want / trade） */
  kind: string
}

type Block = { type: 'section'; name: string; count: number; h: number } | { type: 'row'; cards: Card[]; h: number }

function cardBorder(card: Card): string {
  return card.memberIds.length === 1 ? MEMBER_BY_ID[card.memberIds[0]].color : '#8a8a86'
}

/** 文字が幅に収まらなければ「…」で切る */
function fit(ctx: CanvasRenderingContext2D, text: string, width: number): string {
  if (ctx.measureText(text).width <= width) return text
  let t = text
  while (t.length > 0 && ctx.measureText(t + '…').width > width) t = t.slice(0, -1)
  return t + '…'
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

export async function makeListImages(opt: ListImageOptions, onProgress?: (done: number, total: number) => void): Promise<File[]> {
  const cols = opt.columns
  const gap = cols >= 5 ? 8 : 14
  const cw = (W - PAD * 2 - gap * (cols - 1)) / cols
  const ch = (cw * 85) / 55
  const labelH = opt.labels ? 52 : 0
  const rowH = ch + labelH + gap
  const HEAD = 130
  const FOOT = 60

  // 並べ方を決める（見出し・カードの段）
  const blocks: Block[] = []
  for (const g of opt.groups) {
    blocks.push({ type: 'section', name: g.name, count: g.cards.length, h: 56 })
    for (let i = 0; i < g.cards.length; i += cols) blocks.push({ type: 'row', cards: g.cards.slice(i, i + cols), h: rowH })
  }
  // 画像ごとに分ける（見出しだけがページの最後に残らないようにする）
  const pages: Block[][] = [[]]
  let used = HEAD + FOOT
  for (const [i, b] of blocks.entries()) {
    const next = blocks[i + 1]
    const need = b.type === 'section' && next ? b.h + next.h : b.h
    if (used + need > MAX_H && pages[pages.length - 1].length > 0) {
      pages.push([])
      used = HEAD + FOOT
    }
    pages[pages.length - 1].push(b)
    used += b.h
  }

  const total = opt.groups.reduce((n, g) => n + g.cards.length, 0)
  const d = new Date()
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
  const files: File[] = []
  let done = 0
  for (const [p, page] of pages.entries()) {
    const H = HEAD + page.reduce((n, b) => n + b.h, 0) + FOOT
    const canvas = document.createElement('canvas')
    canvas.width = W
    canvas.height = H
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = BG
    ctx.fillRect(0, 0, W, H)

    // 見出し：黒い四角に「求」、メンバー名・コレクション名、枚数
    ctx.fillStyle = INK
    roundRect(ctx, PAD, 36, 64, 64, 14)
    ctx.fill()
    ctx.fillStyle = BG
    ctx.font = `800 40px ${FONT}`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(opt.mark, PAD + 32, 69)
    ctx.textAlign = 'left'
    ctx.fillStyle = INK
    ctx.font = `800 40px ${FONT}`
    const right = `${total} 枚${pages.length > 1 ? `（${p + 1}/${pages.length}）` : ''}`
    ctx.font = `600 26px ${FONT}`
    const rw = ctx.measureText(right).width
    ctx.fillStyle = MUTED
    ctx.textAlign = 'right'
    ctx.fillText(right, W - PAD, 70)
    ctx.textAlign = 'left'
    ctx.fillStyle = INK
    ctx.font = `800 40px ${FONT}`
    ctx.fillText(fit(ctx, opt.title, W - PAD * 2 - 90 - rw - 20), PAD + 88, 69)

    let y = HEAD
    for (const b of page) {
      if (b.type === 'section') {
        ctx.textBaseline = 'alphabetic'
        ctx.font = `700 28px ${FONT}`
        ctx.fillStyle = INK
        const count = `${b.count} 枚`
        ctx.font = `600 22px ${FONT}`
        const cwid = ctx.measureText(count).width
        ctx.fillStyle = MUTED
        ctx.textAlign = 'right'
        ctx.fillText(count, W - PAD, y + 40)
        ctx.textAlign = 'left'
        ctx.font = `700 28px ${FONT}`
        ctx.fillStyle = INK
        ctx.fillText(fit(ctx, b.name, W - PAD * 2 - cwid - 20), PAD, y + 40)
        y += b.h
        continue
      }
      // 1 段の画像はまとめて読む（1 枚ずつ待つと遅い。全部を一度に読むと iPhone のメモリが足りなくなる）
      const bmps = await Promise.all(b.cards.map((c) => loadBitmap(c, cols)))
      for (const [i, card] of b.cards.entries()) {
        const x = PAD + i * (cw + gap)
        drawCard(ctx, card, bmps[i], x, y, cw, ch)
        if (opt.labels) {
          ctx.textAlign = 'center'
          ctx.textBaseline = 'alphabetic'
          ctx.fillStyle = INK
          ctx.font = `700 ${cols >= 5 ? 17 : 20}px ${FONT}`
          ctx.fillText(fit(ctx, memberLabel(card.memberIds), cw), x + cw / 2, y + ch + 22)
          ctx.fillStyle = MUTED
          ctx.font = `500 ${cols >= 5 ? 15 : 17}px ${FONT}`
          ctx.fillText(fit(ctx, [card.source, card.version].filter(Boolean).join(' '), cw), x + cw / 2, y + ch + 44)
          ctx.textAlign = 'left'
        }
        onProgress?.(++done, total)
      }
      y += b.h
    }

    // 下の小さな文字
    ctx.textBaseline = 'alphabetic'
    ctx.font = `600 20px ${FONT}`
    ctx.fillStyle = MUTED
    ctx.textAlign = 'right'
    ctx.fillText(`pocamaster ・ ${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`, W - PAD, H - 24)
    ctx.textAlign = 'left'

    const blob = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob((bl) => (bl ? resolve(bl) : reject(new Error('画像を作れませんでした'))), 'image/jpeg', 0.9),
    )
    // iPhone で大きな画像を続けて作ると覚えておける量を超えるので、使い終わったら手放す
    canvas.width = 0
    canvas.height = 0
    const suffix = pages.length > 1 ? `-${p + 1}` : ''
    files.push(new File([blob], `pocamaster-${opt.kind}-${stamp}${suffix}.jpg`, { type: 'image/jpeg' }))
  }
  return files
}

/** カードの画像を読む。横 3 枚なら大きい画像、それより細かければ一覧用の小さい画像で足りる。読めなければ undefined（仮カードにする） */
async function loadBitmap(card: Card, cols: number): Promise<ImageBitmap | undefined> {
  if (!card.imageId) return undefined
  try {
    const blob = await (cols <= 3 ? getFull(card.imageId) : getThumb(card.imageId))
    return blob ? await createImageBitmap(blob) : undefined
  } catch {
    return undefined
  }
}

function drawCard(ctx: CanvasRenderingContext2D, card: Card, bmp: ImageBitmap | undefined, x: number, y: number, w: number, h: number) {
  const r = 10
  ctx.save()
  roundRect(ctx, x, y, w, h, r)
  ctx.clip()
  if (bmp) {
    const s = Math.max(w / bmp.width, h / bmp.height)
    const dw = bmp.width * s
    const dh = bmp.height * s
    ctx.drawImage(bmp, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh)
    bmp.close()
  } else {
    // 仮カード：メンバーの色をうすく塗り、名前と入手元を書く
    const members = [...card.memberIds].sort((a, b) => memberOrder(a) - memberOrder(b))
    ctx.fillStyle = members.length === 1 ? MEMBER_BY_ID[members[0]].color + '40' : '#e2e2de'
    ctx.fillRect(x, y, w, h)
    ctx.fillStyle = INK
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    const names = card.memberIds.length === MEMBERS.length ? ['全員'] : memberNames(card.memberIds)
    // 名前（ユニットは 1 人 1 行）を真ん中より少し上に、その下に入手元・バージョン
    const lineH = w / 7
    const top = y + h * 0.42 - ((names.length - 1) * lineH) / 2
    ctx.font = `700 ${Math.round(w / 8)}px ${FONT}`
    names.forEach((n, i) => ctx.fillText(fit(ctx, n, w - 12), x + w / 2, top + i * lineH))
    const below = top + (names.length - 1) * lineH + lineH * 0.9
    ctx.font = `500 ${Math.round(w / 12)}px ${FONT}`
    ctx.fillText(fit(ctx, card.source, w - 12), x + w / 2, below)
    if (card.version) ctx.fillText(fit(ctx, card.version, w - 12), x + w / 2, below + w / 9)
    ctx.textAlign = 'left'
  }
  ctx.restore()
  // メンバーの色の枠
  ctx.strokeStyle = cardBorder(card)
  ctx.lineWidth = 3
  roundRect(ctx, x + 1.5, y + 1.5, w - 3, h - 3, r - 1)
  ctx.stroke()
}

/** iPhone では共有シート（「画像を保存」・X など）を開き、使えなければ 1 枚ずつダウンロードする */
export async function shareFiles(files: File[]): Promise<void> {
  if (navigator.canShare?.({ files })) {
    try {
      await navigator.share({ files })
      return
    } catch (e) {
      if ((e as Error).name === 'AbortError') throw e
    }
  }
  for (const f of files) {
    const url = URL.createObjectURL(f)
    const a = document.createElement('a')
    a.href = url
    a.download = f.name
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
  }
}
