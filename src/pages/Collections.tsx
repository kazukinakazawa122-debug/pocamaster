import { watchScroll } from '../lib/scrollMemory'
import { useEffect, useLayoutEffect, useMemo } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { Link, useNavigationType, useSearchParams } from 'react-router-dom'
import { IconCrown, IconPhoto, IconPlus } from '@tabler/icons-react'
import { COLLECTION_TYPES, db, type Collection } from '../lib/db'
import { useAllCards } from '../lib/cardStore'
import { isComplete, pctText, type Progress } from '../lib/stats'
import { MiniveLoading } from '../components/Minive'
import { ProgressBar, TopBar, useCoverUrl, warmCovers } from '../components/ui'

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

// 「すべて」のときの並び：アルバム（韓国盤・日本盤をまとめて）→ シーグリ → ファンミ → ツアー → そのほか。
// 同じグループの中は発売日の新しい順（本人の要望、2026-09-30）
const GROUP: Record<string, number> = {
  'アルバム（韓国盤）': 0,
  'アルバム（日本盤）': 0,
  シーズングリーティング: 1,
  'ファンミ・ファンコン': 2,
  'ライブ・ツアー': 3,
}
const groupOf = (c: Collection) => GROUP[c.type] ?? 4

// 一覧に戻ってきたとき、読み込み中に白い画面にならないよう、前回の内容とスクロール位置を覚えておく
let lastCollections: Collection[] | undefined
let lastScrollY = 0

async function loadCollections(): Promise<Collection[]> {
  const collections = await db.collections.toArray()
  // ジャケットをまとめて読んでから出す（文字だけ先に出て、あとからジャケットが 1 枚ずつ現れる、をなくす）
  await warmCovers(collections.map((c) => c.coverImageId))
  return collections
}

const EMPTY: Progress = { owned: 0, total: 0, pct: null }

export default function Collections() {
  // 絞り込み（韓国盤・日本盤など）は URL に入れておく。アルバムを開いて「戻る」で来ても、同じ絞り込みのままになる
  const [params, setParams] = useSearchParams()
  const t = params.get('t')
  const filter: (typeof FILTERS)[number] = FILTERS.find((f) => f === t) ?? 'すべて'
  const setFilter = (f: (typeof FILTERS)[number]) => {
    setParams(f === 'すべて' ? {} : { t: f }, { replace: true })
    window.scrollTo(0, 0)
  }
  const live = useLiveQuery(loadCollections)
  if (live) lastCollections = live
  const collections = live ?? lastCollections
  // コレクションごとの枚数は、手元のカードの記録から数える（開くたびに 6,000 枚分を読まない。2026-10-02）
  const cards = useAllCards()
  const byCollection = useMemo(() => {
    const count = new Map<string, Progress>()
    for (const c of cards ?? []) {
      const n = count.get(c.collectionId) ?? { owned: 0, total: 0, pct: null }
      n.total++
      if (c.status === '所持中') n.owned++
      count.set(c.collectionId, n)
    }
    for (const n of count.values()) n.pct = Math.floor((n.owned / n.total) * 100)
    return count
  }, [cards])
  const data = collections && cards ? { collections, byCollection } : undefined

  // 「戻る」で来たときは前回のスクロール位置に戻す。スクロールするたびに位置を覚える
  const back = useNavigationType() === 'POP'
  const ready = !!data
  useLayoutEffect(() => {
    if (ready) window.scrollTo(0, back ? lastScrollY : 0)
  }, [ready, back])
  useEffect(() => watchScroll((y) => (lastScrollY = y)), [])

  if (!data) return <MiniveLoading />

  const list = data.collections
    .filter((c) => filter === 'すべて' || c.type === filter)
    .sort((a, b) => groupOf(a) - groupOf(b) || b.releaseDate.localeCompare(a.releaseDate) || b.createdAt - a.createdAt)

  return (
    <div className="page">
      <TopBar title="コレクション" minive="park" menu>
        <Link className="icon-btn" to="/collections/new" aria-label="コレクションを追加">
          <IconPlus size={24} />
        </Link>
      </TopBar>
      {/* 下にスクロールしても「すべて・韓国盤…」が上に残るよう固定する（本人の要望、2026-10-01） */}
      <div className="chips sticky-chips">
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
        list.map((c) => <Row key={c.id} col={c} p={data.byCollection.get(c.id) ?? EMPTY} />)
      )}
    </div>
  )
}

function Row({ col, p }: { col: Collection; p: Progress }) {
  const url = useCoverUrl(col.coverImageId)
  const done = isComplete(p)
  return (
    <Link to={`/collections/${col.id}`} className="list-item">
      <div className="cover">{url ? <img src={url} alt="" /> : <IconPhoto size={24} aria-hidden />}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="col-name" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{col.name}</span>
          {done && <IconCrown size={18} color="#D4A017" aria-label="コンプリート" style={{ flex: 'none' }} />}
        </div>
        <div className="xs muted col-meta">
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
