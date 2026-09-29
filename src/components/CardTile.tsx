import { useRef } from 'react'
import type { Card } from '../lib/db'
import { MEMBER_BY_ID, memberLabel, memberNames, memberOrder } from '../lib/members'
import { useImageUrl, useNearScreen } from './ui'

const LONG_PRESS_MS = 450

/** 仮カードの枠と背景。ユニットカードは写っているメンバーの色を縞にする */
export function cardColors(card: Card): { border: string; background: string } {
  const members = [...card.memberIds].sort((a, b) => memberOrder(a) - memberOrder(b)).map((id) => MEMBER_BY_ID[id])
  if (members.length === 1) return { border: members[0].color, background: members[0].color + '40' }
  const stripe = 8
  const stops = members.map((m, i) => `${m.color}55 ${i * stripe}px ${(i + 1) * stripe}px`).join(', ')
  return { border: 'var(--text-2)', background: `repeating-linear-gradient(135deg, ${stops})` }
}

interface Props {
  card: Card
  collectionName: string
  /** 6 枚並びのときは仮カードにメンバー名だけを出す */
  compact?: boolean
  onTap: () => void
  onLongPress: () => void
}

/** タップで状態を切り替え、長押しで拡大を開く */
export default function CardTile({ card, collectionName, compact, onTap, onLongPress }: Props) {
  const ref = useRef<HTMLButtonElement>(null)
  // 画面の近くにあるときだけ画像を読み込む（離れたら手放す）
  const near = useNearScreen(ref)
  const url = useImageUrl(near ? card.imageId : undefined, 'thumb')
  const timer = useRef<number | undefined>(undefined)
  const longPressed = useRef(false)
  const start = useRef<{ x: number; y: number } | null>(null)
  const { border, background } = cardColors(card)
  const owned = card.status === '所持中'
  const name = memberLabel(card.memberIds)

  const cancel = () => {
    window.clearTimeout(timer.current)
    start.current = null
  }

  return (
    <button
      ref={ref}
      type="button"
      className={`poca${owned ? '' : ' off'}`}
      style={{ borderColor: border, background }}
      aria-label={`${name} ${card.source} ${card.version} ${card.status}`}
      aria-pressed={owned}
      onPointerDown={(e) => {
        longPressed.current = false
        start.current = { x: e.clientX, y: e.clientY }
        timer.current = window.setTimeout(() => {
          longPressed.current = true
          onLongPress()
        }, LONG_PRESS_MS)
      }}
      onPointerMove={(e) => {
        // スクロールしたら長押しにしない
        if (start.current && Math.hypot(e.clientX - start.current.x, e.clientY - start.current.y) > 8) cancel()
      }}
      onPointerUp={cancel}
      onPointerLeave={cancel}
      onPointerCancel={cancel}
      onContextMenu={(e) => e.preventDefault()}
      onClick={() => {
        if (longPressed.current) return
        onTap()
      }}
    >
      {url ? (
        <img src={url} alt="" decoding="async" />
      ) : card.imageId ? null : (
        <span className="ph">
          {compact ? (
            // 6 枚並びでも名前を 1 行に収める（ユニットは 1 人 1 行）
            memberNames(card.memberIds).map((n) => (
              <span key={n} className="ph-name">
                {n}
              </span>
            ))
          ) : (
            <>
              <span className="xs muted">{collectionName}</span>
              <span className="small" style={{ fontWeight: 700 }}>
                {name}
              </span>
              <span className="xs">{card.source}</span>
              {card.version && <span className="xs muted">{card.version}</span>}
            </>
          )}
        </span>
      )}
    </button>
  )
}
