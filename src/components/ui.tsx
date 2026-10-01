import { useEffect, useState, type ReactNode, type RefObject } from 'react'
import { useNavigate } from 'react-router-dom'
import { IconChevronLeft, IconUser } from '@tabler/icons-react'
import { getFull, getThumb, type Profile } from '../lib/db'
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
export function useNearScreen(ref: RefObject<Element | null>, margin = 800): boolean {
  const [near, setNear] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el || typeof IntersectionObserver === 'undefined') {
      setNear(true)
      return
    }
    return watchNear(el, margin, setNear)
  }, [ref, margin])
  return near
}

// カード 1 枚ごとに監視を作ると数百個になって重いので、同じ余白の監視は 1 つを使い回す
const watchers = new Map<number, { io: IntersectionObserver; cbs: Map<Element, (near: boolean) => void> }>()
function watchNear(el: Element, margin: number, cb: (near: boolean) => void): () => void {
  let w = watchers.get(margin)
  if (!w) {
    const cbs = new Map<Element, (near: boolean) => void>()
    const io = new IntersectionObserver(
      (entries) => {
        // 同じ要素の通知が続いたときは、いちばん新しい状態だけを使う
        for (const e of entries) cbs.get(e.target)?.(e.isIntersecting)
      },
      { rootMargin: `${margin}px 0px` },
    )
    w = { io, cbs }
    watchers.set(margin, w)
  }
  const { io, cbs } = w
  cbs.set(el, cb)
  io.observe(el)
  return () => {
    cbs.delete(el)
    io.unobserve(el)
  }
}

/** プロフィールのアイコン（丸）。枠は推しメンの色にしない（本人の要望、2026-10-01） */
export function ProfileAvatar({ profile, size }: { profile?: Profile; size: number }) {
  const url = useImageUrl(profile?.imageId, 'thumb')
  return (
    <span className="avatar" style={{ width: size, height: size, borderColor: 'var(--line)' }}>
      {url ? <img src={url} alt="" /> : <IconUser size={size * 0.55} aria-hidden />}
    </span>
  )
}

/** 保存した画像を表示用の URL にする（'thumb' は一覧用の小さい画像だけを読む） */
export function useImageUrl(imageId: string | undefined, size: 'thumb' | 'full'): string | undefined {
  const [url, setUrl] = useState<string>()
  useEffect(() => {
    if (!imageId) {
      setUrl(undefined)
      return
    }
    let objectUrl: string | undefined
    let alive = true
    ;(size === 'thumb' ? getThumb(imageId) : getFull(imageId)).then((blob) => {
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
