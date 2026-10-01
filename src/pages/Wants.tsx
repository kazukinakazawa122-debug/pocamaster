import { useMemo, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { IconAdjustmentsHorizontal } from '@tabler/icons-react'
import { db } from '../lib/db'
import { MEMBER_BY_ID, MEMBERS, type MemberId } from '../lib/members'
import { TopBar } from '../components/ui'
import CardGroups, { type CardGroup } from '../components/CardGroups'
import { MiniveLoading } from '../components/Minive'

interface WantsView {
  member: MemberId | 'all'
  /** コレクションの id。'all' なら全部 */
  collection: string
  favoritesOnly: boolean
  imagesOnly: boolean
  columns: number
  labels: boolean
}

const DEFAULT_VIEW: WantsView = { member: 'all', collection: 'all', favoritesOnly: false, imagesOnly: true, columns: 4, labels: false }
const VIEW_KEY = 'wantsView'

// 選んだ絞り込みは、次に開いたときも同じにする（この端末だけ）
function loadView(): WantsView {
  try {
    return { ...DEFAULT_VIEW, ...JSON.parse(localStorage.getItem(VIEW_KEY) ?? '{}') }
  } catch {
    return DEFAULT_VIEW
  }
}

/**
 * 求めているカード（F-25、本人の要望 2026-10-01）：持っていないカードだけを、メンバー・コレクションで絞って並べる。
 * 交換や譲ってもらうときに、スクショして見せる用。持っていないカードも暗くしない
 */
export default function Wants() {
  const [view, setViewState] = useState<WantsView>(loadView)
  const [showFilters, setShowFilters] = useState(true)
  const setView = (patch: Partial<WantsView>) => {
    const next = { ...view, ...patch }
    setViewState(next)
    try {
      localStorage.setItem(VIEW_KEY, JSON.stringify(next))
    } catch {
      /* 保存できなくても表示は変える */
    }
  }

  const data = useLiveQuery(async () => {
    const [collections, cards] = await Promise.all([db.collections.toArray(), db.cards.where('status').equals('未所持').toArray()])
    return { collections, cards }
  })
  const collections = useMemo(
    () => [...(data?.collections ?? [])].sort((a, b) => b.releaseDate.localeCompare(a.releaseDate)),
    [data],
  )
  const groups = useMemo(() => {
    if (!data) return []
    const byCol = new Map<string, CardGroup>(collections.map((col) => [col.id, { col, cards: [] }]))
    for (const c of data.cards) {
      if (view.member !== 'all' && !c.memberIds.includes(view.member)) continue
      if (view.collection !== 'all' && c.collectionId !== view.collection) continue
      if (view.favoritesOnly && !c.favorite) continue
      if (view.imagesOnly && !c.imageId) continue
      byCol.get(c.collectionId)?.cards.push(c)
    }
    const list = [...byCol.values()].filter((g) => g.cards.length > 0)
    list.forEach((g) => g.cards.sort((a, b) => a.order - b.order))
    return list
  }, [data, collections, view])
  const count = groups.reduce((n, g) => n + g.cards.length, 0)
  const m = view.member === 'all' ? null : MEMBER_BY_ID[view.member]
  const colName = view.collection === 'all' ? null : collections.find((c) => c.id === view.collection)?.name

  return (
    <div className="page">
      <TopBar title="求めているカード" back menu>
        <button
          className="icon-btn"
          aria-label={showFilters ? '絞り込みを隠す' : '絞り込みを出す'}
          aria-expanded={showFilters}
          onClick={() => setShowFilters(!showFilters)}
        >
          <IconAdjustmentsHorizontal size={22} />
        </button>
      </TopBar>

      {showFilters && (
        <div className="panel stack" style={{ marginBottom: 12 }}>
          <div className="chips">
            <button className={`chip${view.member === 'all' ? ' on' : ''}`} onClick={() => setView({ member: 'all' })}>
              全員
            </button>
            {MEMBERS.map((mm) => {
              const on = view.member === mm.id
              return (
                <button
                  key={mm.id}
                  className="chip"
                  style={on ? { background: mm.color, borderColor: mm.color, color: mm.on } : { color: mm.text }}
                  onClick={() => setView({ member: mm.id })}
                >
                  {mm.name}
                </button>
              )
            })}
          </div>
          <label className="field" style={{ marginBottom: 0 }}>
            <span>コレクション</span>
            <select value={view.collection} onChange={(e) => setView({ collection: e.target.value })}>
              <option value="all">すべてのコレクション</option>
              {collections.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <div className="chips" style={{ flexWrap: 'wrap' }}>
            <button className={`chip${view.favoritesOnly ? ' on' : ''}`} aria-pressed={view.favoritesOnly} onClick={() => setView({ favoritesOnly: !view.favoritesOnly })}>
              お気に入りだけ
            </button>
            <button className={`chip${view.imagesOnly ? ' on' : ''}`} aria-pressed={view.imagesOnly} onClick={() => setView({ imagesOnly: !view.imagesOnly })}>
              画像のあるカードだけ
            </button>
            <button className={`chip${view.labels ? ' on' : ''}`} aria-pressed={view.labels} onClick={() => setView({ labels: !view.labels })}>
              名前を出す
            </button>
          </div>
          <div className="chips" role="group" aria-label="横に並べる枚数">
            {[3, 4, 5, 6].map((n) => (
              <button key={n} className={`chip${view.columns === n ? ' on' : ''}`} onClick={() => setView({ columns: n })}>
                横 {n} 枚
              </button>
            ))}
          </div>
          <div className="xs muted">
            カードを押すと「所持中」になり、この一覧から消えます（すぐ下の「元に戻す」で戻せます）。長押しで大きく見られます。
            右上の <IconAdjustmentsHorizontal size={12} aria-hidden style={{ verticalAlign: -2 }} /> で、この絞り込みを隠せます（スクショ用）。
          </div>
        </div>
      )}

      {/* スクショしたときに何の一覧かわかる見出し */}
      <div className="wants-head">
        <span className="wants-mark">求</span>
        <span style={m ? { color: m.text } : undefined}>{m ? m.name : '全員'}</span>
        {colName && <span className="muted">・{colName}</span>}
        <span className="muted num" style={{ marginLeft: 'auto', fontSize: 13 }}>
          {count} 枚
        </span>
      </div>

      {!data ? (
        <MiniveLoading />
      ) : count === 0 ? (
        <div className="empty">{data.cards.length === 0 ? '持っていないカードはありません' : 'この絞り込みに合うカードはありません'}</div>
      ) : (
        <CardGroups key={JSON.stringify(view)} groups={groups} columns={view.columns} bright labels={view.labels} />
      )}
    </div>
  )
}
