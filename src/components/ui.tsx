import { useEffect, useState, type ReactNode, type RefObject } from 'react'
import { useNavigate } from 'react-router-dom'
import { IconChevronLeft, IconUser } from '@tabler/icons-react'
import { db, type Profile } from '../lib/db'
import { MiniveRun, type MiniveStyle } from './Minive'

export function ProgressBar({ pct, color = 'var(--all)' }: { pct: number | null; color?: string }) {
  return (
    <div className="bar" role="progressbar" aria-valuenow={pct ?? 0} aria-valuemin={0} aria-valuemax={100}>
      <i style={{ width: `${pct ?? 0}%`, background: color }} />
    </div>
  )
}

export function TopBar({ title, back, minive, children }: { title: string; back?: boolean; minive?: MiniveStyle; children?: ReactNode }) {
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
    const io = new IntersectionObserver(([e]) => setNear(e.isIntersecting), { rootMargin: `${margin}px 0px` })
    io.observe(el)
    return () => io.disconnect()
  }, [ref, margin])
  return near
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

/** 保存した画像を表示用の URL にする */
export function useImageUrl(imageId: string | undefined, size: 'thumb' | 'full'): string | undefined {
  const [url, setUrl] = useState<string>()
  useEffect(() => {
    if (!imageId) {
      setUrl(undefined)
      return
    }
    let objectUrl: string | undefined
    let alive = true
    db.images.get(imageId).then((img) => {
      if (!alive || !img) return
      objectUrl = URL.createObjectURL(img[size])
      setUrl(objectUrl)
    })
    return () => {
      alive = false
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [imageId, size])
  return url
}
