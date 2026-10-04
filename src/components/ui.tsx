import { useEffect, useState, type ReactNode, type RefObject } from 'react'
import { useNavigate } from 'react-router-dom'
import { IconChevronLeft, IconUser } from '@tabler/icons-react'
import { db, getFull, getThumb, type Profile } from '../lib/db'
import { MiniveRun, type MiniveStyle } from './Minive'
import { MenuButton } from './SideMenu'

export function ProgressBar({ pct, color = 'var(--all)' }: { pct: number | null; color?: string }) {
  return (
    <div className="bar" role="progressbar" aria-valuenow={pct ?? 0} aria-valuemin={0} aria-valuemax={100}>
      <i style={{ width: `${pct ?? 0}%`, background: color }} />
    </div>
  )
}

/** 上のバー。menu で右上に 3 本線（サイドバー）を出す（タブの画面と、サイドバーから行く画面） */
export function TopBar({ title, back, minive, menu, children }: { title: string; back?: boolean; minive?: MiniveStyle; menu?: boolean; children?: ReactNode }) {
  const navigate = useNavigate()
  return (
    <>
      <header className="topbar">
        {back && (
          <button className="icon-btn" aria-label="戻る" onClick={() => navigate(-1)}>
            <IconChevronLeft size={24} />
          </button>
        )}
        <h1 style={minive ? { flex: 'none' } : undefined}>{title}</h1>
        {minive && <MiniveRun style={minive} />}
        {children}
        {menu && <MenuButton />}
      </header>
      <div className="topbar-space" />
    </>
  )
}

export function Sheet({ onClose, children }: { onClose: () => void; children: ReactNode }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])
  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <div className="sheet" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  )
}

/**
 * 要素が画面の近く（上下 margin 以内）にあるか。
 * 画面から離れたカードの画像は読み込まない・手放すために使う（iPhone で画像が多いと落ちるため）
 */
export function useNearScreen(ref: RefObject<Element | null>, margin = 800, axis: 'y' | 'x' = 'y'): boolean {
  const [near, setNear] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el || typeof IntersectionObserver === 'undefined') {
      setNear(true)
      return
    }
    return watchNear(el, margin, axis, setNear)
  }, [ref, margin, axis])
  return near
}

// カード 1 枚ごとに監視を作ると数百個になって重いので、同じ余白の監視は 1 つを使い回す
const watchers = new Map<string, { io: IntersectionObserver; cbs: Map<Element, (near: boolean) => void> }>()
function watchNear(el: Element, margin: number, axis: 'y' | 'x', cb: (near: boolean) => void): () => void {
  const wk = `${axis}${margin}`
  let w = watchers.get(wk)
  if (!w) {
    const cbs = new Map<Element, (near: boolean) => void>()
    const io = new IntersectionObserver(
      (entries) => {
        // 同じ要素の通知が続いたときは、いちばん新しい状態だけを使う
        for (const e of entries) cbs.get(e.target)?.(e.isIntersecting)
      },
      // 縦に並ぶ一覧は上下に、横に並ぶ一覧（ホームのお気に入りなど）は左右に、余白をとる
      { rootMargin: axis === 'y' ? `${margin}px 0px` : `0px ${margin}px` },
    )
    w = { io, cbs }
    watchers.set(wk, w)
  }
  const { io, cbs } = w
  cbs.set(el, cb)
  io.observe(el)
  return () => {
    cbs.delete(el)
    io.unobserve(el)
  }
}

/**
 * ジャケット（コレクションの表紙）とプロフィールのアイコンの URL は、アプリを閉じるまで覚えておく
 * （本人の報告、2026-10-01「ジャケットの画像が出るのがかなり遅い」：一覧を開くたびに 1 枚ずつ読み直していた）。
 * 数が少ない（約 40 枚）ので覚えておいても軽い。カードの画像（数千枚）は覚えない
 */
const keptUrls = new Map<string, string>()
const KEEP_MAX = 300

/** ジャケットを 1 回でまとめて読んでおく（1 枚ずつ読むと iPhone では遅い）。読み終わってから一覧を出せば、文字と同時に出る */
export async function warmCovers(ids: (string | undefined)[]): Promise<void> {
  const need = [...new Set(ids.filter((id): id is string => !!id && !keptUrls.has(id)))]
  if (need.length === 0 || keptUrls.size + need.length > KEEP_MAX) return
  const thumbs = await db.thumbs.bulkGet(need)
  // 一覧用の小さい画像を分ける前に取り込んだ表紙は images の中にある
  const missing = need.filter((_, i) => !thumbs[i])
  const old = missing.length ? await db.images.bulkGet(missing) : []
  thumbs.forEach((t, i) => t && keptUrls.set(need[i], URL.createObjectURL(t.thumb)))
  old.forEach((img, i) => {
    const blob = img?.thumb ?? img?.full
    if (blob) keptUrls.set(missing[i], URL.createObjectURL(blob))
  })
}

/** ジャケット・アイコン用：覚えておいた URL があればすぐ返す。なければ読んで覚える（手放さない） */
export function useCoverUrl(imageId: string | undefined): string | undefined {
  const [url, setUrl] = useState(() => (imageId ? keptUrls.get(imageId) : undefined))
  useEffect(() => {
    if (!imageId) {
      setUrl(undefined)
      return
    }
    const kept = keptUrls.get(imageId)
    if (kept) {
      setUrl(kept)
      return
    }
    let alive = true
    getThumb(imageId).then((blob) => {
      if (!blob) return
      // 同じ画像をほかの場所が先に読んでいたら、それを使う
      let u = keptUrls.get(imageId)
      if (!u) {
        u = URL.createObjectURL(blob)
        if (keptUrls.size < KEEP_MAX) keptUrls.set(imageId, u)
      }
      if (alive) setUrl(u)
    })
    return () => {
      alive = false
    }
  }, [imageId])
  return url
}

/** プロフィールのアイコン（丸）。枠は推しメンの色にしない（本人の要望、2026-10-01） */
export function ProfileAvatar({ profile, size }: { profile?: Profile; size: number }) {
  const url = useCoverUrl(profile?.imageId)
  return (
    <span className="avatar" style={{ width: size, height: size, borderColor: 'var(--line)' }}>
      {url ? <img src={url} alt="" /> : <IconUser size={size * 0.55} aria-hidden />}
    </span>
  )
}

/**
 * 一覧用の小さい画像は、まとめて読む（本人の報告、2026-10-02「まだ読み込みが長い」）。
 * カード 1 枚ごとに読みに行くと、画面に出る数十枚の分だけ読む回数が増え、iPhone では遅い。
 * 同じ瞬間に頼まれた分を 1 回で読み、最近の THUMB_KEEP 枚は覚えておく（戻ってきたときに読み直さない）
 */
const THUMB_KEEP = 500
const thumbKept = new Map<string, Blob>()
let thumbQueue = new Map<string, ((b: Blob | undefined) => void)[]>()
let thumbFlushScheduled = false

function keepThumb(id: string, blob: Blob) {
  thumbKept.delete(id)
  thumbKept.set(id, blob)
  // 古いものから捨てる（Map は入れた順に並ぶ）
  if (thumbKept.size > THUMB_KEEP) thumbKept.delete(thumbKept.keys().next().value!)
}

async function flushThumbs() {
  thumbFlushScheduled = false
  const batch = thumbQueue
  thumbQueue = new Map()
  const ids = [...batch.keys()]
  let blobs: (Blob | undefined)[] = []
  try {
    const rows = await db.thumbs.bulkGet(ids)
    // 一覧用の小さい画像を分ける前に取り込んだ画像は images の中にある
    const missing = ids.filter((_, i) => !rows[i])
    const old = missing.length ? await db.images.bulkGet(missing) : []
    const oldById = new Map(missing.map((id, i) => [id, old[i]?.thumb ?? old[i]?.full]))
    blobs = ids.map((id, i) => rows[i]?.thumb ?? oldById.get(id))
  } catch {
    /* 読めなければ画像なしで出す */
  }
  ids.forEach((id, i) => {
    const b = blobs[i]
    if (b) keepThumb(id, b)
    batch.get(id)!.forEach((resolve) => resolve(b))
  })
}

function loadThumb(id: string): Promise<Blob | undefined> {
  const kept = thumbKept.get(id)
  if (kept) {
    keepThumb(id, kept)
    return Promise.resolve(kept)
  }
  return new Promise((resolve) => {
    const waiting = thumbQueue.get(id)
    if (waiting) waiting.push(resolve)
    else thumbQueue.set(id, [resolve])
    if (!thumbFlushScheduled) {
      thumbFlushScheduled = true
      // 同じ描き直しで頼まれた分（画面に出るカード全部）を集めてから読む
      queueMicrotask(flushThumbs)
    }
  })
}

/**
 * 一覧用の画像の仮 URL（createObjectURL）は、作るのが重い（IndexedDB の画像では 1 回ごとに約 1ms。スクロールで数百回、
 * 本人の報告「ラグ」の調査で、起動・スクロール・ホームの切り替えの処理時間の大きな部分だった。2026-10-04）。
 * 手放すたびに作り直さず、最近の THUMB_URL_KEEP 枚の URL を使い回す。使っている間（refs > 0）は手放さない
 */
const THUMB_URL_KEEP = 400
const thumbUrls = new Map<string, { url: string; refs: number }>() // 入れた順（＝使った順）に並ぶ

function evictThumbUrls() {
  if (thumbUrls.size <= THUMB_URL_KEEP) return
  for (const [id, e] of thumbUrls) {
    if (thumbUrls.size <= THUMB_URL_KEEP) break
    if (e.refs > 0) continue // 画面で使っているものは手放さない
    URL.revokeObjectURL(e.url)
    thumbUrls.delete(id)
  }
}

/** 覚えている URL を使い始める（使った順を新しくする）。なければ undefined */
function takeThumbUrl(id: string): string | undefined {
  const e = thumbUrls.get(id)
  if (!e) return undefined
  e.refs++
  thumbUrls.delete(id)
  thumbUrls.set(id, e)
  return e.url
}

function addThumbUrl(id: string, blob: Blob): string {
  const known = takeThumbUrl(id)
  if (known) return known
  const url = URL.createObjectURL(blob)
  thumbUrls.set(id, { url, refs: 1 })
  evictThumbUrls()
  return url
}

function releaseThumbUrl(id: string) {
  const e = thumbUrls.get(id)
  if (e && e.refs > 0) e.refs--
}

/** 保存した画像を表示用の URL にする（'thumb' は一覧用の小さい画像だけを、まとめて読む。URL は使い回す） */
export function useImageUrl(imageId: string | undefined, size: 'thumb' | 'full'): string | undefined {
  const [url, setUrl] = useState<string>()
  useEffect(() => {
    if (!imageId) {
      setUrl(undefined)
      return
    }
    let alive = true
    if (size === 'thumb') {
      let held = false
      // 覚えている URL があれば、読まずにすぐ使う
      const known = takeThumbUrl(imageId)
      if (known) {
        held = true
        setUrl(known)
      } else {
        loadThumb(imageId).then((blob) => {
          if (!alive || !blob) return
          held = true
          setUrl(addThumbUrl(imageId, blob))
        })
      }
      return () => {
        alive = false
        if (held) releaseThumbUrl(imageId)
        setUrl(undefined)
      }
    }
    let objectUrl: string | undefined
    getFull(imageId).then((blob) => {
      if (!alive || !blob) return
      objectUrl = URL.createObjectURL(blob)
      setUrl(objectUrl)
    })
    return () => {
      alive = false
      if (objectUrl) URL.revokeObjectURL(objectUrl)
      // 手放した URL を使い続けると壊れた画像が一瞬出るので、空にしておく
      setUrl(undefined)
    }
  }, [imageId, size])
  return url
}
