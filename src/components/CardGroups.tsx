import { useCallback, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { setCardStatus, type Card, type CardStatus, type Collection } from '../lib/db'
import { memberLabel } from '../lib/members'
import CardTile from './CardTile'
import CardSheet from './CardSheet'
import { useUndo } from './Undo'

export interface CardGroup {
  col: Collection
  cards: Card[]
}

/** 一度に出す枚数（多すぎると iPhone で重いので、残りは「もっと見る」で出す） */
const PAGE = 240

interface Props {
  groups: CardGroup[]
  /** 横に並べる枚数 */
  columns?: number
  /** 持っていなくても暗くしない */
  bright?: boolean
  /** カードの下にメンバー・入手元・バージョンを出す */
  labels?: boolean
  /** 押したら状態を切り替えずに拡大を開く（「譲」の一覧：押しただけで未所持にならないように） */
  tapOpens?: boolean
}

/**
 * いくつものコレクションのカードを、コレクションごとの見出しを付けて並べる（検索・求めているカード）。
 * タップで状態を切り替え（「元に戻す」付き）、長押しで拡大
 */
export default function CardGroups({ groups, columns = 3, bright, labels = true, tapOpens }: Props) {
  const [limit, setLimit] = useState(PAGE)
  const [openId, setOpenId] = useState<string | null>(null)
  const showUndo = useUndo()
  // カードに渡す関数は毎回同じものを使う（変わっていないカードを描き直さないため）
  const toggleRef = useRef<(card: Card) => void>(() => {})
  const onTap = useCallback((c: Card) => toggleRef.current(c), [])
  const onLongPress = useCallback((c: Card) => setOpenId(c.id), [])
  const toggle = (card: Card) => {
    const to: CardStatus = card.status === '所持中' ? '未所持' : '所持中'
    setCardStatus(card, to)
    showUndo(`${memberLabel(card.memberIds)} を${to}にしました`, () => setCardStatus({ ...card, status: to }, card.status))
  }
  toggleRef.current = tapOpens ? (c: Card) => setOpenId(c.id) : toggle

  // 「もっと見る」までの枚数で切る
  let left = limit
  const shown: CardGroup[] = []
  for (const g of groups) {
    if (left <= 0) break
    shown.push({ col: g.col, cards: g.cards.slice(0, left) })
    left -= g.cards.length
  }
  const total = groups.reduce((n, g) => n + g.cards.length, 0)
  const open = openId ? groups.flatMap((g) => g.cards.map((c) => ({ c, col: g.col }))).find((x) => x.c.id === openId) : undefined

  return (
    <>
      {shown.map(({ col, cards }) => (
        <section key={col.id}>
          <div className="row-head">
            <Link to={`/collections/${col.id}`} style={{ fontWeight: 700 }}>
              {col.name}
            </Link>
            <span className="muted num">{groups.find((g) => g.col.id === col.id)!.cards.length} 枚</span>
          </div>
          <div className="card-grid" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`, gap: columns >= 5 ? 4 : 8 }}>
            {cards.map((c) => (
              <div key={c.id}>
                <CardTile card={c} collectionName={col.name} compact={columns >= 5} bright={bright} onTap={onTap} onLongPress={onLongPress} />
                {labels && (
                  <div className="tile-label">
                    {memberLabel(c.memberIds)}
                    <br />
                    {[c.source, c.version].filter(Boolean).join(' ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      ))}
      {total > limit && (
        <button className="btn block" style={{ marginTop: 16 }} onClick={() => setLimit(limit + PAGE)}>
          もっと見る（残り {total - limit} 枚）
        </button>
      )}
      {open && <CardSheet card={open.c} collectionName={open.col.name} onClose={() => setOpenId(null)} onToggle={() => toggle(open.c)} />}
    </>
  )
}
