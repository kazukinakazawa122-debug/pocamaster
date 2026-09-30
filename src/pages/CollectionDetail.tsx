import { useEffect, useLayoutEffect, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { Link, useNavigationType, useParams, useSearchParams } from 'react-router-dom'
import { IconEdit, IconLayoutGridAdd, IconPin, IconPinFilled, IconPlus } from '@tabler/icons-react'
import { db, setCardStatus, type Card, type CardStatus } from '../lib/db'
import { MEMBER_BY_ID, MEMBERS, memberLabel, memberOrder, type MemberId } from '../lib/members'
import { memberProgress, pctText, progress } from '../lib/stats'
import { ProgressBar, TopBar } from '../components/ui'
import CardTile from '../components/CardTile'
import CardSheet from '../components/CardSheet'
import { useUndo } from '../components/Undo'

const STATUS_FILTERS = ['すべて', '未所持', '所持中'] as const

/** コレクションごとのスクロール位置（カードの編集などから「戻る」で来たときに元の位置に戻す） */
const scrollById = new Map<string, number>()

/** ソロを先にメンバー順、そのあとユニット */
function byMember(a: Card, b: Card): number {
  if (a.memberIds.length !== b.memberIds.length) return a.memberIds.length - b.memberIds.length
  return memberOrder(a.memberIds[0]) - memberOrder(b.memberIds[0])
}

type Row = { key: string; source: string; version: string; all: Card[]; shown: Card[] }

/**
 * 1 段に 1 枚しかない段をまとめる（本人の要望）。
 * - 番号がメンバーごとに違うカード（AMUSE ウエハース2 の N-01〜N-06 など）
 * - メンバーごとに品物が違うグッズ（IVE SCOUT の Rug・Hoodie など）。データの並びで離れていても 1 段にする
 * 同じ入手元の「1 人 1 枚の段」を、メンバーが重ならない範囲で 6 枚まで、最初に出てきた位置にまとめる
 */
function mergeNumbered(rows: Row[]): Row[] {
  type Group = { rows: Row[]; members: Set<string> }
  const out: (Row | Group)[] = []
  const open = new Map<string, Group[]>() // 入手元 → まだ入るまとまり
  for (const r of rows) {
    const single = r.all.length === 1 && r.all[0].memberIds.length === 1
    if (!single) {
      out.push(r)
      continue
    }
    const m = r.all[0].memberIds[0]
    const list = open.get(r.source) ?? []
    let g = list.find((x) => x.rows.length < MEMBERS.length && !x.members.has(m))
    if (!g) {
      g = { rows: [], members: new Set() }
      list.push(g)
      open.set(r.source, list)
      out.push(g)
    }
    g.rows.push(r)
    g.members.add(m)
  }
  return out.map((x) => {
    if (!('members' in x)) return x
    const group = x.rows
    if (group.length === 1) return group[0]
    const first = group[0]
    const last = group[group.length - 1]
    // 番号の並び（N-01 など）なら「N-01〜N-06」、品物の名前なら「メンバーごとのグッズ」
    const numbered = group.every((g) => /\d+$/.test(g.version))
    return {
      key: first.key,
      source: first.source,
      version: numbered ? `${first.version}〜${last.version}` : 'メンバーごとのグッズ',
      all: group.flatMap((g) => g.all),
      shown: group.flatMap((g) => g.shown).sort(byMember),
    }
  })
}

export default function CollectionDetail() {
  const { id = '' } = useParams()
  const [params, setParams] = useSearchParams()
  const memberParam = (params.get('m') as MemberId | null) ?? null
  const status = (params.get('s') as (typeof STATUS_FILTERS)[number] | null) ?? 'すべて'
  const [openCardId, setOpenCardId] = useState<string | null>(null)
  const showUndo = useUndo()

  const data = useLiveQuery(async () => {
    const [col, cards] = await Promise.all([db.collections.get(id), db.cards.where('collectionId').equals(id).sortBy('order')])
    return { col, cards }
  }, [id])

  const back = useNavigationType() === 'POP'
  const ready = !!data
  useLayoutEffect(() => {
    if (ready) window.scrollTo(0, back ? (scrollById.get(id) ?? 0) : 0)
  }, [ready, back, id])
  useEffect(() => {
    const onScroll = () => scrollById.set(id, window.scrollY)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [id])

  if (!data) return <div className="page empty">読み込み中…</div>
  const { col, cards } = data
  if (!col) return <div className="page empty">コレクションが見つかりません</div>

  const setParam = (key: string, value: string | null) => {
    const next = new URLSearchParams(params)
    if (value === null) next.delete(key)
    else next.set(key, value)
    setParams(next, { replace: true })
  }

  const toggle = (card: Card) => {
    const to: CardStatus = card.status === '所持中' ? '未所持' : '所持中'
    setCardStatus(card, to)
    showUndo(`${memberLabel(card.memberIds)} を${to}にしました`, () => setCardStatus({ ...card, status: to }, card.status))
  }

  // カードに出てくるメンバーだけタブにする。1 人だけ（個人のコレクション）なら「全員」タブを出さない
  const present = MEMBERS.filter((mm) => cards.some((c) => c.memberIds.includes(mm.id)))
  const tabs = present.length > 0 ? present : MEMBERS
  const solo = present.length === 1
  const member = solo ? present[0].id : memberParam && tabs.some((t) => t.id === memberParam) ? memberParam : null

  const total = progress(cards)
  const memberCards = member ? cards.filter((c) => c.memberIds.includes(member)) : cards
  const visible = memberCards.filter((c) => status === 'すべて' || c.status === status)
  const m = member ? MEMBER_BY_ID[member] : null
  const openCard = cards.find((c) => c.id === openCardId)

  // 「全員」タブ：入手元＋バージョンごとの段にする（最初に出てきた順）
  const rows: Row[] = []
  if (!member) {
    const index = new Map<string, number>()
    for (const c of cards) {
      const key = `${c.source}\u0000${c.version}`
      if (!index.has(key)) {
        index.set(key, rows.length)
        rows.push({ key, source: c.source, version: c.version, all: [], shown: [] })
      }
      const row = rows[index.get(key)!]
      row.all.push(c)
      if (status === 'すべて' || c.status === status) row.shown.push(c)
    }
    rows.forEach((r) => r.shown.sort(byMember))
  }
  const grouped = member ? rows : mergeNumbered(rows)

  const tile = (c: Card, compact: boolean) => (
    <CardTile key={c.id} card={c} collectionName={col.name} compact={compact} onTap={() => toggle(c)} onLongPress={() => setOpenCardId(c.id)} />
  )

  return (
    <div className="page">
      <TopBar title={col.name} back>
        <Link className="icon-btn" to={`/collections/${id}/bulk`} aria-label="カードをまとめて追加">
          <IconLayoutGridAdd size={22} />
        </Link>
        <Link className="icon-btn" to={`/collections/${id}/cards/new`} aria-label="カードを追加">
          <IconPlus size={22} />
        </Link>
        <Link className="icon-btn" to={`/collections/${id}/edit`} aria-label="コレクションを編集">
          <IconEdit size={22} />
        </Link>
      </TopBar>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <span className="num" style={{ fontSize: 24, fontWeight: 700 }}>
          {pctText(total)}
        </span>
        <div style={{ flex: 1 }}>
          <ProgressBar pct={total.pct} />
        </div>
        <span className="small muted num">
          {total.owned} / {total.total}
        </span>
        <button
          className={`chip${col.pinned ? ' on' : ''}`}
          aria-pressed={!!col.pinned}
          onClick={() => db.collections.update(col.id, { pinned: !col.pinned })}
          style={{ display: 'inline-flex', alignItems: 'center', gap: 2 }}
        >
          {col.pinned ? <IconPinFilled size={14} aria-hidden /> : <IconPin size={14} aria-hidden />}
          {col.pinned ? 'ホームに表示中' : 'ホームに出す'}
        </button>
      </div>

      <div className="chips" style={{ marginBottom: 8 }}>
        {!solo && (
          <button className={`chip${!member ? ' on' : ''}`} onClick={() => setParam('m', null)}>
            全員
          </button>
        )}
        {tabs.map((mm) => {
          const on = member === mm.id
          return (
            <button
              key={mm.id}
              className="chip"
              style={on ? { background: mm.color, borderColor: mm.color, color: mm.on } : { color: mm.text }}
              onClick={() => setParam('m', mm.id)}
            >
              {mm.name}
            </button>
          )
        })}
      </div>
      <div className="chips" style={{ marginBottom: 4 }}>
        {STATUS_FILTERS.map((s) => (
          <button key={s} className={`chip${status === s ? ' on' : ''}`} onClick={() => setParam('s', s === 'すべて' ? null : s)}>
            {s}
          </button>
        ))}
      </div>

      {m && !solo && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '8px 0' }}>
          <span className="small" style={{ color: m.text, fontWeight: 700 }}>
            {m.name}
          </span>
          <div style={{ flex: 1 }}>
            <ProgressBar pct={memberProgress(cards, m.id).pct} color={m.color} />
          </div>
          <span className="small num">{pctText(memberProgress(cards, m.id))}</span>
        </div>
      )}

      {cards.length === 0 ? (
        <div className="empty">
          <p>カードの枠を作りましょう</p>
          <Link className="btn primary" to={`/collections/${id}/bulk`}>
            まとめて追加
          </Link>
        </div>
      ) : visible.length === 0 ? (
        <div className="empty">該当するカードはありません</div>
      ) : solo ? (
        // 個人のコレクション：入手元ごとの段に横 3 枚で並べる
        [...new Set(visible.map((c) => c.source))].map((source) => {
          const all = cards.filter((c) => c.source === source)
          return (
            <section key={source}>
              <div className="row-head">
                <span style={{ fontWeight: 700 }}>{source}</span>
                <span className="muted num">
                  {progress(all).owned}/{all.length}
                </span>
              </div>
              <div className="grid-3">
                {visible
                  .filter((c) => c.source === source)
                  .map((c) => (
                    <div key={c.id}>
                      {tile(c, false)}
                      {c.version && <div className="tile-label">{c.version}</div>}
                    </div>
                  ))}
              </div>
            </section>
          )
        })
      ) : member ? (
        <div className="grid-3" style={{ marginTop: 8 }}>
          {visible.map((c) => (
            <div key={c.id}>
              {tile(c, false)}
              <div className="tile-label">
                {c.source}
                {c.version && <br />}
                {c.version}
              </div>
            </div>
          ))}
        </div>
      ) : (
        grouped
          .filter((r) => r.shown.length > 0)
          .map((r) => (
            <section key={r.key}>
              <div className="row-head">
                <span style={{ fontWeight: 700 }}>
                  {r.source} <span className="muted" style={{ fontWeight: 400 }}>{r.version}</span>
                </span>
                <span className="muted num">
                  {progress(r.all).owned}/{r.all.length}
                </span>
              </div>
              <div className="grid-6">{r.shown.map((c) => tile(c, true))}</div>
            </section>
          ))
      )}

      {openCard && <CardSheet card={openCard} collectionName={col.name} onClose={() => setOpenCardId(null)} onToggle={() => toggle(openCard)} />}
    </div>
  )
}
