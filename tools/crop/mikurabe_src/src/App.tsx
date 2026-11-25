import { useEffect, useMemo, useRef, useState } from "react";

// 見比べチェック：左＝新しい写真、右＝前の画像。「ちがう」だけ押す。
// db: checks/<id> {v:"ng"}（Claude が読む）・meta/seen {ids}・meta/pos {id}・meta/done {at, ng}
type Item = { id: string; round: string; group: string; sheet: string; no: number; member: string; source: string; version: string; img: string; flag: boolean };
type Data = { title: string; items: Item[] };

const DATA: Data = (() => {
  try { return JSON.parse(document.getElementById("data")!.textContent || ""); } catch { return { title: "見比べチェック", items: [] }; }
})();
const ITEMS = DATA.items;
const LS = "mikurabe:" + DATA.title;

function lsGet(k: string) { try { return JSON.parse(localStorage.getItem(LS + k) || "null"); } catch { return null; } }
function lsSet(k: string, v: unknown) { try { localStorage.setItem(LS + k, JSON.stringify(v)); } catch { /* なくても動く */ } }

type DB = any;

export default function App() {
  const [ng, setNg] = useState<Record<string, true>>(() => lsGet("ng") || {});
  const [seen, setSeen] = useState<Set<string>>(() => new Set(lsGet("seen") || []));
  const [done, setDone] = useState<string | null>(null);
  const [group, setGroup] = useState<string>("all");
  const [onlyNg, setOnlyNg] = useState(false);
  const [status, setStatus] = useState("保存先に接続しています…");
  const db = useRef<DB>(null);
  const restored = useRef(false);
  const lastPos = useRef<string | null>(lsGet("pos"));
  const seenTimer = useRef<number | undefined>(undefined);
  const seenRef = useRef(seen);
  seenRef.current = seen;

  const groups = useMemo(() => {
    const order: string[] = [];
    const by: Record<string, Item[]> = {};
    for (const it of ITEMS) {
      const g = it.group;
      if (!by[g]) { by[g] = []; order.push(g); }
      by[g].push(it);
    }
    return order.map((g) => ({ name: g, items: by[g] }));
  }, []);

  // 保存先（db）につなぐ。なければこの端末に残す
  useEffect(() => {
    let off: (() => void)[] = [];
    (async () => {
      let d: DB = null;
      try { d = (window as any).claude?.use ? await (window as any).claude.use("db") : null; } catch { d = null; }
      if (!d) { setStatus("この画面では Claude への保存ができません。押した結果はこの端末にだけ残ります。"); restore(); return; }
      db.current = d;
      const timer = window.setTimeout(() => setStatus("保存先につながるのを待っています。押した結果はつながりしだい保存されます。"), 10000);
      off.push(d.collection("checks").onSnapshot((snap: any) => {
        const m: Record<string, true> = {};
        for (const doc of snap.docs) if (doc.data()?.v === "ng") m[doc.id] = true;
        setNg(m); lsSet("ng", m);
        if (!snap.metadata.fromCache) { clearTimeout(timer); setStatus(""); }
      }, (e: any) => { clearTimeout(timer); setStatus("保存先につながりませんでした（" + (e?.code || "error") + "）。ページを開き直してください。"); }));
      off.push(d.collection("meta").onSnapshot((snap: any) => {
        for (const doc of snap.docs) {
          const v = doc.data() || {};
          if (doc.id === "seen" && Array.isArray(v.ids)) setSeen((s) => { const n = new Set(s); v.ids.forEach((x: string) => n.add(x)); return n; });
          if (doc.id === "pos" && typeof v.id === "string" && !restored.current) lastPos.current = v.id;
          if (doc.id === "done") setDone(v.at || null);
        }
        if (!snap.metadata.fromCache) restore();
      }, () => restore()));
    })();
    return () => off.forEach((f) => f());
  }, []);

  // 開き直したら、前に見ていた組へ
  function restore() {
    if (restored.current) return;
    restored.current = true;
    const id = lastPos.current;
    if (!id) return;
    requestAnimationFrame(() => document.getElementById("c-" + id)?.scrollIntoView({ block: "start" }));
  }

  // 画面に出た組を「見た」にする
  useEffect(() => {
    const io = new IntersectionObserver((es) => {
      const add: string[] = [];
      for (const e of es) if (e.isIntersecting) add.push((e.target as HTMLElement).dataset.id!);
      if (!add.length) return;
      setSeen((s) => {
        if (add.every((x) => s.has(x))) return s;
        const n = new Set(s); add.forEach((x) => n.add(x)); return n;
      });
      if (restored.current) {
        lastPos.current = add[add.length - 1];
        lsSet("pos", lastPos.current);
      }
      window.clearTimeout(seenTimer.current);
      seenTimer.current = window.setTimeout(() => {
        const ids = [...seenRef.current];
        lsSet("seen", ids);
        db.current?.collection("meta").doc("seen").set({ ids }).catch(() => {});
        if (lastPos.current) db.current?.collection("meta").doc("pos").set({ id: lastPos.current }).catch(() => {});
      }, 1500);
    }, { threshold: 0.6 });
    document.querySelectorAll("[data-id]").forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [group, onlyNg]);

  function toggle(id: string) {
    const was = !!ng[id];
    const m = { ...ng };
    if (was) delete m[id]; else m[id] = true;
    setNg(m); lsSet("ng", m);
    const ref = db.current?.collection("checks").doc(id);
    if (ref) (was ? ref.delete() : ref.set({ v: "ng", at: new Date().toISOString() }))
      .catch((e: any) => setStatus("保存できませんでした（" + (e?.code || "error") + "）。もう一度押してください。"));
  }

  function finish() {
    const at = new Date().toISOString();
    setDone(at);
    const ids = [...seen];
    lsSet("seen", ids);
    db.current?.collection("meta").doc("seen").set({ ids }).catch(() => {});
    db.current?.collection("meta").doc("done").set({ at, ng: Object.keys(ng).length, seen: ids.length })
      .catch((e: any) => setStatus("保存できませんでした（" + (e?.code || "error") + "）。もう一度押してください。"));
  }

  const ngCount = ITEMS.filter((i) => ng[i.id]).length;
  const seenCount = ITEMS.filter((i) => seen.has(i.id)).length;
  const shown = groups
    .filter((g) => group === "all" || g.name === group)
    .map((g) => ({ ...g, items: g.items.filter((i) => !onlyNg || ng[i.id]) }))
    .filter((g) => g.items.length);

  return (
    <div className="min-h-screen bg-paper text-ink">
      <header className="sticky top-0 z-10 border-b border-line bg-surface pt-[env(safe-area-inset-top)]">
        <div className="mx-auto max-w-[720px] px-4 py-2.5">
          <div className="flex items-baseline justify-between gap-3">
            <h1 className="font-display text-[17px] font-bold">{DATA.title}</h1>
            <p className="text-[13px] tabular-nums text-muted">
              ちがう <b className="text-ng">{ngCount}</b>・見た <b className="text-ink">{seenCount}</b>/{ITEMS.length}
            </p>
          </div>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-paper" aria-hidden>
            <div className="h-full bg-ink transition-[width]" style={{ width: (ITEMS.length ? (seenCount / ITEMS.length) * 100 : 0) + "%" }} />
          </div>
          <div className="-mx-4 mt-2 flex gap-2 overflow-x-auto px-4 pb-0.5 [scrollbar-width:none]">
            <Chip on={group === "all"} onClick={() => { setGroup("all"); scrollTo(0, 0); }}>全部</Chip>
            {groups.map((g) => {
              const s = g.items.filter((i) => seen.has(i.id)).length;
              const n = g.items.filter((i) => ng[i.id]).length;
              return (
                <Chip key={g.name} on={group === g.name} onClick={() => { setGroup(g.name); scrollTo(0, 0); }}>
                  {g.name} <span className="tabular-nums opacity-70">{s}/{g.items.length}</span>
                  {n > 0 && <span className="ml-1 tabular-nums text-ng">✕{n}</span>}
                </Chip>
              );
            })}
          </div>
          <label className="mt-2 flex min-h-[36px] items-center gap-2 text-[14px]">
            <input type="checkbox" className="size-5 accent-[var(--ng)]" checked={onlyNg} onChange={(e) => setOnlyNg(e.target.checked)} />
            「ちがう」にした組だけ出す
          </label>
          {status && <p className="text-[12px] text-muted">{status}</p>}
        </div>
      </header>

      <main className="mx-auto max-w-[720px] px-4 pb-16">
        <p className="mt-4 text-[14px] text-muted">左が新しい写真、右が前の画像です。ちがうカードのときだけ「ちがう」を押してください。押さない組は「合っている」になります。</p>
        {shown.length === 0 && <p className="py-8 text-center text-muted">この条件の組はありません。</p>}
        {shown.map((g) => (
          <section key={g.name}>
            <h2 className="mb-2.5 mt-7 font-display text-[16px] font-bold">{g.name} <span className="font-sans text-[12px] font-normal text-muted">{g.items.length} 組</span></h2>
            <div className="flex flex-col gap-3.5">
              {g.items.map((it) => {
                const bad = !!ng[it.id];
                return (
                  <article key={it.id} id={"c-" + it.id} data-id={it.id}
                    className={"scroll-mt-[190px] rounded-xl border-2 bg-surface p-3 " + (bad ? "border-ng" : "border-line")}>
                    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                      <span className="font-bold tabular-nums text-ink">{it.sheet} の {it.no}</span>
                      <span className="font-bold">{it.member}</span>
                      <span className="text-[13px] text-muted [overflow-wrap:anywhere]">{(it.source + " " + it.version).trim()}</span>
                      {it.flag && <span className="rounded-full bg-flagbg px-2 text-[12px] text-flag">前の画像がぼかし・特に見てください</span>}
                    </div>
                    <img className="mt-2 block h-auto w-full rounded-md bg-paper" src={it.img} alt={it.member + " の新しい写真と前の画像"} />
                    <div className="mt-1 grid grid-cols-2 text-center text-[12px] text-muted"><span>新しい写真</span><span>前の画像</span></div>
                    <button type="button" aria-pressed={bad} onClick={() => toggle(it.id)}
                      className={"mt-2.5 min-h-[56px] w-full rounded-lg border-2 text-[17px] font-bold active:scale-[.99] " +
                        (bad ? "border-ng bg-ng text-white" : "border-line bg-surface text-ng")}>
                      {bad ? "ちがう（押すと取り消し）" : "ちがう"}
                    </button>
                  </article>
                );
              })}
            </div>
          </section>
        ))}
        <div className="mt-10 rounded-xl border border-line bg-surface p-4">
          <p className="text-[14px]">最後まで見たら押してください。「ちがう」は {ngCount} 組です。</p>
          <button type="button" onClick={finish}
            className="mt-3 min-h-[56px] w-full rounded-lg bg-ink text-[17px] font-bold text-surface active:scale-[.99]">
            {done ? "見終えました（もう一度押せます）" : "見終えた"}
          </button>
          {done && <p className="mt-2 text-[13px] text-muted">Claude に伝わります。チャットで「やりました」と送ってください。</p>}
        </div>
      </main>
    </div>
  );
}

function Chip({ on, onClick, children }: { on: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button type="button" aria-pressed={on} onClick={onClick}
      className={"min-h-[40px] shrink-0 whitespace-nowrap rounded-full border px-3.5 text-[14px] " +
        (on ? "border-ink bg-ink text-surface" : "border-line bg-surface text-ink")}>
      {children}
    </button>
  );
}
