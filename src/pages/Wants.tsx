import { useEffect, useMemo, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { IconAdjustmentsHorizontal, IconPhoto, IconShare } from '@tabler/icons-react'
import { db } from '../lib/db'
import { MEMBER_BY_ID, MEMBERS, type MemberId } from '../lib/members'
import { TopBar } from '../components/ui'
import CardGroups, { type CardGroup } from '../components/CardGroups'
import { MiniveLoading } from '../components/Minive'
import { makeListImages, shareFiles } from '../lib/listImage'

interface WantsView {
  /** want＝求めている（持っていない）カード、trade＝譲れるカード（「譲」の印を付けた、持っているカード） */
  mode: 'want' | 'trade'
  member: MemberId | 'all'
  /** コレクションの id。'all' なら全部 */
  collection: string
  favoritesOnly: boolean
  imagesOnly: boolean
  columns: number
  labels: boolean
}

const DEFAULT_VIEW: WantsView = { mode: 'want', member: 'all', collection: 'all', favoritesOnly: false, imagesOnly: true, columns: 4, labels: false }
const VIEW_KEY = 'wantsView'
/** 画像にできるカードの枚数（横 4 枚で画像 4〜5 枚ほど） */
const IMAGE_LIMIT = 300

// 選んだ絞り込みは、次に開いたときも同じにする（この端末だけ）
function loadView(): WantsView {
  try {
    return { ...DEFAULT_VIEW, ...JSON.parse(localStorage.getItem(VIEW_KEY) ?? '{}') }
  } catch {
    return DEFAULT_VIEW
  }
}

/**
 * 求・譲の一覧（F-25、本人の要望 2026-10-01）：交換で見せる用。メンバー・コレクションで絞って並べ、スクショか画像にする。
 * 求＝持っていないカード（暗くしない）。譲＝「譲」の印を付けた、持っているカード
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

  const trade = view.mode === 'trade'
  const data = useLiveQuery(async () => {
    const [collections, cards] = await Promise.all([
      db.collections.toArray(),
      trade ? db.cards.where('status').equals('所持中').filter((c) => !!c.trade).toArray() : db.cards.where('status').equals('未所持').toArray(),
    ])
    return { collections, cards }
  }, [trade])
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
  const mark = trade ? '譲' : '求'

  // 一覧の画像（2026-10-01）。iPhone の共有シートはタップの直後でないと開けないので、作るのと保存・共有を 2 回のタップに分ける
  const [images, setImages] = useState<File[] | null>(null)
  const [making, setMaking] = useState('')
  const [imageError, setImageError] = useState('')
  const listKey = `${JSON.stringify(view)}|${count}`
  // 一覧が変わったら作った画像は古くなるので消す
  useEffect(() => setImages(null), [listKey])
  const previews = useMemo(() => images?.map((f) => URL.createObjectURL(f)) ?? [], [images])
  useEffect(() => () => previews.forEach((u) => URL.revokeObjectURL(u)), [previews])
  const makeImages = async () => {
    setImageError('')
    // 多すぎると画像が何十枚にもなり、iPhone では時間がかかって途中で止まることもあるので、絞ってもらう
    if (count > IMAGE_LIMIT) {
      setImageError(`${count} 枚は多すぎるので、メンバーやコレクションで ${IMAGE_LIMIT} 枚以下に絞ってね`)
      return
    }
    setMaking('画像を作っています…')
    try {
      const files = await makeListImages(
        {
          mark,
          title: [m ? m.name : '全員', colName].filter(Boolean).join('・'),
          groups: groups.map((g) => ({ name: g.col.name, cards: g.cards })),
          columns: view.columns,
          labels: view.labels,
          kind: trade ? 'trade' : 'want',
        },
        // 1 枚ごとに書き換えると一覧の画面ごと描き直して遅くなるので、12 枚ごとにする
        (done, total) => (done % 12 === 0 || done === total) && setMaking(`画像を作っています… ${done} / ${total}`),
      )
      setImages(files)
    } catch (e) {
      setImageError(`画像を作れなかった：${(e as Error).message}`)
    } finally {
      setMaking('')
    }
  }

  return (
    <div className="page">
      <TopBar title="求・譲の一覧" back menu>
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
          <div className="chips" role="group" aria-label="どちらの一覧">
            <button className={`chip${!trade ? ' on' : ''}`} onClick={() => setView({ mode: 'want' })}>
              求めているカード
            </button>
            <button className={`chip${trade ? ' on' : ''}`} onClick={() => setView({ mode: 'trade' })}>
              譲れるカード
            </button>
          </div>
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
          {count > 0 &&
            (images ? (
              <>
                <button
                  className="btn primary block"
                  onClick={() => shareFiles(images).catch((e) => (e as Error).name !== 'AbortError' && setImageError((e as Error).message))}
                >
                  <IconShare size={20} aria-hidden />
                  画像を保存・共有する{images.length > 1 ? `（${images.length} 枚）` : ''}
                </button>
                <div className="list-previews">
                  {previews.map((u, i) => (
                    <img key={u} src={u} alt={`できた画像 ${i + 1}`} />
                  ))}
                </div>
              </>
            ) : (
              <button className="btn block" disabled={!!making} onClick={makeImages}>
                <IconPhoto size={20} aria-hidden />
                {making || 'この一覧を画像にする'}
              </button>
            ))}
          {imageError && <div className="error" style={{ margin: 0 }}>{imageError}</div>}
        </div>
      )}

      {/* スクショしたときに何の一覧かわかる見出し */}
      <div className="wants-head">
        <span className="wants-mark">{mark}</span>
        <span style={m ? { color: m.text } : undefined}>{m ? m.name : '全員'}</span>
        {colName && <span className="muted">・{colName}</span>}
        <span className="muted num" style={{ marginLeft: 'auto', fontSize: 13 }}>
          {count} 枚
        </span>
      </div>

      {!data ? (
        <MiniveLoading />
      ) : count === 0 ? (
        <div className="empty">
          {data.cards.length > 0
            ? 'この絞り込みに合うカードはないみたい'
            : trade
              ? '「譲」のカードはまだないよ。カードを長押しして「譲」を押すと、ここに並ぶ'
              : '持っていないカードはないみたい'}
        </div>
      ) : (
        <CardGroups key={JSON.stringify(view)} groups={groups} columns={view.columns} bright labels={view.labels} tapOpens={trade} />
      )}
    </div>
  )
}
