import { useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { db, type Card } from '../lib/db'
import { MEMBERS, memberOrder, type MemberId } from '../lib/members'
import CardTile from './CardTile'
import { Sheet } from './ui'

/**
 * マイアルバムに入れるカードを選ぶ。
 * 最初は「所持中」だけを出す。未所持も出すときは、枚数が多い（5,000 枚以上）のでコレクションを選んでもらう
 */
export default function CardPicker({ onPick, onClose }: { onPick: (card: Card) => void; onClose: () => void }) {
  const [collectionId, setCollectionId] = useState('')
  const [member, setMember] = useState<MemberId | null>(null)
  const [ownedOnly, setOwnedOnly] = useState(true)

  const collections = useLiveQuery(() => db.collections.orderBy('releaseDate').toArray())
  const cards = useLiveQuery(async () => {
    if (!ownedOnly && !collectionId) return []
    let list = collectionId ? await db.cards.where('collectionId').equals(collectionId).toArray() : await db.cards.where('status').equals('所持中').toArray()
    if (ownedOnly) list = list.filter((c) => c.status === '所持中')
    return list
  }, [collectionId, ownedOnly])
  const colName = new Map((collections ?? []).map((c) => [c.id, c.name]))
  const colOrder = new Map((collections ?? []).map((c, i) => [c.id, i]))

  const shown = (cards ?? [])
    .filter((c) => !member || c.memberIds.includes(member))
    .sort(
      (a, b) =>
        (colOrder.get(a.collectionId) ?? 0) - (colOrder.get(b.collectionId) ?? 0) ||
        a.memberIds.length - b.memberIds.length ||
        memberOrder(a.memberIds[0]) - memberOrder(b.memberIds[0]) ||
        a.order - b.order,
    )

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
      <div className="chips" style={{ marginBottom: 10 }}>
        <button className={`chip${ownedOnly ? ' on' : ''}`} onClick={() => setOwnedOnly(true)}>
          所持中だけ
        </button>
        <button className={`chip${!ownedOnly ? ' on' : ''}`} onClick={() => setOwnedOnly(false)}>
          未所持も出す
        </button>
      </div>

      {!ownedOnly && !collectionId ? (
        <div className="empty small">未所持のカードも出すときは、上でコレクションを選んでください</div>
      ) : !cards ? (
        <div className="empty small">読み込み中…</div>
      ) : shown.length === 0 ? (
        <div className="empty small">{ownedOnly ? '所持中のカードがありません' : 'カードがありません'}</div>
      ) : (
        <div className="grid-3">
          {shown.map((c) => (
            <div key={c.id}>
              <CardTile card={c} collectionName={colName.get(c.collectionId) ?? ''} onTap={() => onPick(c)} onLongPress={() => onPick(c)} />
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
      )}
    </Sheet>
  )
}
