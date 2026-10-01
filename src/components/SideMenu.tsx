import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { NavLink } from 'react-router-dom'
import { IconChartBar, IconChevronRight, IconHeartSearch, IconMenu2, IconSearch, IconX } from '@tabler/icons-react'

/** サイドバーから行ける画面（本人の要望、2026-10-01：右上の 3 本線から開く）。機能が増えたらここに足す */
const ITEMS = [
  { to: '/search', label: 'カードを探す', note: '店の名前・言葉で全部のカードから', Icon: IconSearch },
  { to: '/wants', label: '求・譲の一覧', note: '交換で見せるカードを並べて画像に', Icon: IconHeartSearch },
  { to: '/history', label: '集めた記録', note: '月ごとに増えた枚数のグラフ', Icon: IconChartBar },
]

/** 上のバーの右上の 3 本線。押すと右からサイドバーが出る */
export function MenuButton() {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button className="icon-btn" aria-label="メニュー" aria-expanded={open} onClick={() => setOpen(true)}>
        <IconMenu2 size={24} />
      </button>
      {open && createPortal(<SideMenu onClose={() => setOpen(false)} />, document.body)}
    </>
  )
}

function SideMenu({ onClose }: { onClose: () => void }) {
  const [closing, setClosing] = useState(false)
  // 閉じるときは右へすべって消えるのを待ってから消す（動きを減らす設定でも閉じるよう、時間で待つ）
  const close = () => {
    setClosing(true)
    window.setTimeout(onClose, 200)
  }
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return
      setClosing(true)
      window.setTimeout(onClose, 200)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])
  return (
    <div className={`drawer-backdrop${closing ? ' closing' : ''}`} onClick={close}>
      <nav className="drawer" role="dialog" aria-modal="true" aria-label="メニュー" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-head">
          <span className="drawer-title">メニュー</span>
          <button className="icon-btn" aria-label="閉じる" onClick={close}>
            <IconX size={22} />
          </button>
        </div>
        {ITEMS.map(({ to, label, note, Icon }) => (
          // 画面を移ったら閉じる（アニメーションを待たずにすぐ閉じる）
          <NavLink key={to} to={to} className="drawer-item" onClick={onClose}>
            <span className="drawer-ic">
              <Icon size={22} stroke={1.7} aria-hidden />
            </span>
            <span className="drawer-text">
              <span className="drawer-label">{label}</span>
              <span className="drawer-note">{note}</span>
            </span>
            <IconChevronRight size={18} className="muted" aria-hidden />
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
