import { useEffect, useMemo, useRef, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { db, type Card } from '../lib/db'
import { useAllCards } from '../lib/cardStore'
import { MEMBERS, memberOrder, type MemberId } from '../lib/members'
import CardTile from './CardTile'
import { Sheet } from './ui'

/**
 * はじめに並べる枚数（横 3 枚 × 20 段）。下へ動かして終わりに近づいたら、同じだけ足す。
 * 持っているカード（1,500 枚ほど）を一度に全部並べると、iPhone では出るまで 4 秒ほどかかっていた（2026-10-14）
 */
const STEP = 60

/** マイアルバムに入れるカードを選ぶ。入れられるのは所持中のカードだけ（本人の要望、2026-09-30） */
export default function CardPicker({ onPick, onClose }: { onPick: (card: Card) => void; onClose: () => void }) {
  const [collectionId, setCollectionId] = useState('')
  const [member, setMember] = useState<MemberId | null>(null)
  const [limit, setLimit] = useState(STEP)

  // カードは手元の記録から選ぶ（開くたびに、持っているカードをデータベースから 2 回読み直さない）
  const all = useAllCards()
  const allCollections = useLiveQuery(() => db.collections.orderBy('releaseDate').toArray())
  const owned = useMemo(() => all?.filter((c) => c.status === '所持中'), [all])
  // 所持中のカードがあるコレクションだけを選べるようにする
  const collections = useMemo(() => {
    if (!owned || !allCollections) return undefined
    const ids = new Set(owned.map((c) => c.collectionId))
    return allCollections.filter((c) => ids.has(c.id))
  }, [owned, allCollections])
  const colName = useMemo(() => new Map((collections ?? []).map((c) => [c.id, c.name])), [collections])

  const shown = useMemo(() => {
    const colOrder = new Map((collections ?? []).map((c, i) => [c.id, i]))
    return (owned ?? [])
      .filter((c) => (!collectionId || c.collectionId === collectionId) && (!member || c.memberIds.includes(member)))
      .sort(
        (a, b) =>
          (colOrder.get(a.collectionId) ?? 0) - (colOrder.get(b.collectionId) ?? 0) ||
          a.memberIds.length - b.memberIds.length ||
          memberOrder(a.memberIds[0]) - memberOrder(b.memberIds[0]) ||
          a.order - b.order,
      )
  }, [owned, collections, collectionId, member])

  // 絞り込みを変えたら、はじめの枚数から
  useEffect(() => setLimit(STEP), [collectionId, member])

  // 並べた分の終わりが見えてきたら（下に 600px 以内）、続きを足す。足したあとも見えていれば、さらに足す（作り直すと最初の知らせが来る）
  const endRef = useRef<HTMLDivElement>(null)
  const hasMore = shown.length > limit
  useEffect(() => {
    const el = endRef.current
    if (!el || !hasMore || typeof IntersectionObserver === 'undefined') return
    const io = new IntersectionObserver((entries) => entries.some((e) => e.isIntersecting) && setLimit((n) => n + STEP), {
      root: el.closest('.sheet'),
      rootMargin: '0px 0px 600px 0px',
    })
    io.observe(el)
    return () => io.disconnect()
  }, [hasMore, limit])

  return (
    <Sheet onClose={onClose}>
      <div style={{ width: 36, height: 5, borderRadius: 3, background: 'var(--line)', margin: '0 auto 12px' }} />
      <div style={{ fontWeight: 700, marginBottom: 8 }}>入れるカードを選ぶ</div>

      <label className="field" style={{ marginBottom: 8 }}>
        <select value={collectionId} onChange={(e) => setCollectionId(e.target.value)} aria-label="コレクション">
          <option value="">すべてのコレクション</option>
          {(collections ?? []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </label>
      <div className="chips" style={{ marginBottom: 6 }}>
        <button className={`chip${!member ? ' on' : ''}`} onClick={() => setMember(null)}>
          全員
        </button>
        {MEMBERS.map((m) => (
          <button
            key={m.id}
            className="chip"
            style={member === m.id ? { background: m.color, borderColor: m.color, color: m.on } : { color: m.text }}
            onClick={() => setMember(m.id)}
          >
            {m.name}
          </button>
        ))}
      </div>
      <div className="xs muted" style={{ marginBottom: 10 }}>
        入れられるのは所持中のカードです
      </div>

      {!owned ? (
        <div className="empty small">読み込み中…</div>
      ) : shown.length === 0 ? (
        <div className="empty small">所持中のカードがありません</div>
      ) : (
        <>
          <div className="grid-3">
            {shown.slice(0, limit).map((c) => (
              <div key={c.id}>
                <CardTile card={c} collectionName={colName.get(c.collectionId) ?? ''} onTap={onPick} onLongPress={onPick} />
                <div className="tile-label">
                  {!collectionId && (
                    <>
                      {colName.get(c.collectionId)}
                      <br />
                    </>
                  )}
                  {c.source} {c.version}
                </div>
              </div>
            ))}
          </div>
          {hasMore && <div ref={endRef} style={{ height: 1 }} aria-hidden />}
        </>
      )}
    </Sheet>
  )
}
