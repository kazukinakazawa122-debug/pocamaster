import { useEffect, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { IconChevronLeft } from '@tabler/icons-react'
import { db } from '../lib/db'

export function ProgressBar({ pct, color = 'var(--all)' }: { pct: number | null; color?: string }) {
  return (
    <div className="bar" role="progressbar" aria-valuenow={pct ?? 0} aria-valuemin={0} aria-valuemax={100}>
      <i style={{ width: `${pct ?? 0}%`, background: color }} />
    </div>
  )
}

export function TopBar({ title, back, children }: { title: string; back?: boolean; children?: ReactNode }) {
  const navigate = useNavigate()
  return (
    <header className="topbar">
      {back && (
        <button className="icon-btn" aria-label="戻る" onClick={() => navigate(-1)}>
          <IconChevronLeft size={24} />
        </button>
      )}
      <h1>{title}</h1>
      {children}
    </header>
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
