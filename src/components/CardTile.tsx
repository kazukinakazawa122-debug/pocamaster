import { memo, useRef } from 'react'
import type { Card } from '../lib/db'
import { memberLabel, memberNames } from '../lib/members'
import { useImageUrl, useNearScreen } from './ui'

const LONG_PRESS_MS = 450

/** 仮カードの枠と背景。ユニットカードは写っているメンバーの色を縞にする */
/**
 * カードの縁と下地（2026-11-26、本人の要望で見直し）。
 * 大きな SNS（Instagram・YouTube）の写真のように、縁は目立たない細い線、下地は灰色にして写真だけを目立たせる。
 * メンバーカラーはタブや絞り込みのボタンだけに使い、カードの縁には使わない
 */
export function cardColors(_card: Card): { border: string; background: string } {
  return { border: 'var(--poca-line)', background: 'var(--surface)' }
}

interface Props {
  card: Card
  collectionName: string
  /** 6 枚並びのときは仮カードにメンバー名だけを出す */
  compact?: boolean
  /** 持っていなくても暗くしない（求めているカードの一覧。スクショで見やすくする） */
  bright?: boolean
  /** まとめて選んでいるとき：true＝選んでいる、false＝選んでいない。選ぶ画面でなければ undefined */
  selected?: boolean
  /** 押したカードを渡す（親は同じ関数を使い回せるので、変わっていないカードを描き直さずに済む） */
  onTap: (card: Card) => void
  onLongPress: (card: Card) => void
}

/**
 * 見た目に関わる値が変わっていないカードは描き直さない。
 * 数百枚のコレクションで 1 枚切り替えるたびに全部を描き直すと、iPhone で遅くなるため
 */
function same(a: Props, b: Props): boolean {
  const x = a.card
  const y = b.card
  return (
    x.id === y.id &&
    x.status === y.status &&
    x.imageId === y.imageId &&
    x.trade === y.trade &&
    a.selected === b.selected &&
    x.source === y.source &&
    x.version === y.version &&
    x.memberIds.join() === y.memberIds.join() &&
    a.compact === b.compact &&
    a.bright === b.bright &&
    a.collectionName === b.collectionName &&
    a.onTap === b.onTap &&
    a.onLongPress === b.onLongPress
  )
}

/** タップで状態を切り替え、長押しで拡大を開く */
function CardTileView({ card, collectionName, compact, bright, selected, onTap, onLongPress }: Props) {
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
      // 選んでいるカードは暗くせず、枠と印で示す（暗くすると印も暗くなるため）
      className={`poca${owned || bright || selected ? '' : ' off'}${selected ? ' sel' : ''}`}
      style={{ borderColor: border, background }}
      aria-label={`${name} ${card.source} ${card.version} ${card.status}`}
      aria-pressed={selected ?? owned}
      onPointerDown={(e) => {
        longPressed.current = false
        start.current = { x: e.clientX, y: e.clientY }
        timer.current = window.setTimeout(() => {
          longPressed.current = true
          onLongPress(card)
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
        onTap(card)
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
      {card.trade && owned && (
        <span className="poca-trade" aria-label="譲れる">
          譲
        </span>
      )}
      {selected !== undefined && <span className={`poca-check${selected ? ' on' : ''}`} aria-hidden />}
    </button>
  )
}

export default memo(CardTileView, same)
