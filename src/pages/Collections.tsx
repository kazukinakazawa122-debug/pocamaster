import { useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { Link } from 'react-router-dom'
import { IconCrown, IconPhoto, IconPlus } from '@tabler/icons-react'
import { COLLECTION_TYPES, db, type Card, type Collection } from '../lib/db'
import { isComplete, pctText, progress } from '../lib/stats'
import { ProgressBar, TopBar, useImageUrl } from '../components/ui'

const FILTERS = ['すべて', ...COLLECTION_TYPES] as const
const SHORT: Record<string, string> = {
  'アルバム（韓国盤）': '韓国盤',
  'アルバム（日本盤）': '日本盤',
  シーズングリーティング: 'シーグリ',
  'ファンミ・ファンコン': 'ファンミ',
  'ライブ・ツアー': 'ツアー',
  ノンアルバム: 'NON ALBUM',
  '個人（ソロ）': 'ソロ',
}

export default function Collections() {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>('すべて')
  const data = useLiveQuery(async () => {
    const [collections, cards] = await Promise.all([db.collections.toArray(), db.cards.toArray()])
    const byCollection = new Map<string, Card[]>()
    for (const c of cards) byCollection.set(c.collectionId, [...(byCollection.get(c.collectionId) ?? []), c])
    return { collections, byCollection }
  })
  if (!data) return null

  const list = data.collections
    .filter((c) => filter === 'すべて' || c.type === filter)
    .sort((a, b) => b.releaseDate.localeCompare(a.releaseDate) || b.createdAt - a.createdAt)

  return (
    <div className="page">
      <TopBar title="コレクション">
        <Link className="icon-btn" to="/collections/new" aria-label="コレクションを追加">
          <IconPlus size={24} />
        </Link>
      </TopBar>
      <div className="chips" style={{ marginBottom: 8 }}>
        {FILTERS.map((f) => (
          <button key={f} className={`chip${filter === f ? ' on' : ''}`} onClick={() => setFilter(f)}>
            {SHORT[f] ?? f}
          </button>
        ))}
      </div>
      {list.length === 0 ? (
        <div className="empty">
          <p>このコレクションはまだありません</p>
          <Link className="btn" to="/collections/new">
            コレクションを追加
          </Link>
        </div>
      ) : (
        list.map((c) => <Row key={c.id} col={c} cards={data.byCollection.get(c.id) ?? []} />)
      )}
    </div>
  )
}

function Row({ col, cards }: { col: Collection; cards: Card[] }) {
  const url = useImageUrl(col.coverImageId, 'thumb')
  const p = progress(cards)
  const done = isComplete(p)
  return (
    <Link to={`/collections/${col.id}`} className="list-item">
      <div className="cover">{url ? <img src={url} alt="" /> : <IconPhoto size={24} aria-hidden />}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontWeight: 700 }}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{col.name}</span>
          {done && <IconCrown size={18} color="#D4A017" aria-label="コンプリート" style={{ flex: 'none' }} />}
        </div>
        <div className="xs muted">
          {col.releaseDate || '日付なし'}　{col.type}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
          <div style={{ flex: 1 }}>
            <ProgressBar pct={p.pct} />
          </div>
          <span className="small num" style={{ width: 40, textAlign: 'right' }}>
            {pctText(p)}
          </span>
        </div>
      </div>
    </Link>
  )
}
