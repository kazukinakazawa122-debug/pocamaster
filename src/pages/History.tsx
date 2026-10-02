import { useMemo, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { db } from '../lib/db'
import { useAllCards } from '../lib/cardStore'
import { MEMBER_BY_ID, MEMBERS, memberLabel, type MemberId } from '../lib/members'
import { TopBar } from '../components/ui'
import { MiniveLoading } from '../components/Minive'

/** グラフに出す月の数 */
const MONTHS = 12

function monthKey(ms: number): string {
  const d = new Date(ms)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}
function monthLabel(key: string): string {
  const [y, m] = key.split('-')
  return `${y}年${Number(m)}月`
}
function dayLabel(ms: number): string {
  const d = new Date(ms)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

/**
 * 集めた記録（F-24、本人の要望 2026-10-01）：月ごとに「所持中」が何枚増えたか。
 * 状態を切り替えた記録（statusHistory）から数える。「未所持」に戻したら 1 枚減らす（まちがえて押して戻した分を数えない）
 */
export default function History() {
  const [member, setMember] = useState<MemberId | null>(null)
  const [picked, setPicked] = useState<string | null>(null)
  // カードは手元の記録から（開くたびに 6,000 枚を読み直さない）
  const hc = useLiveQuery(async () => {
    const [history, collections] = await Promise.all([db.statusHistory.orderBy('changedAt').toArray(), db.collections.toArray()])
    return { history, collections }
  })
  const cards = useAllCards()
  const data = useMemo(() => (hc && cards ? { ...hc, cards } : undefined), [hc, cards])

  const view = useMemo(() => {
    if (!data) return null
    const cardById = new Map(data.cards.map((c) => [c.id, c]))
    const colName = new Map(data.collections.map((c) => [c.id, c.name]))
    const history = data.history.filter((h) => !member || cardById.get(h.cardId)?.memberIds.includes(member))
    const net = new Map<string, number>()
    for (const h of history) {
      const d = h.to === '所持中' ? 1 : h.from === '所持中' ? -1 : 0
      if (d) net.set(monthKey(h.changedAt), (net.get(monthKey(h.changedAt)) ?? 0) + d)
    }
    // いまの月から 12 か月さかのぼる（記録のない月も 0 として出す）
    const now = new Date()
    const months: { key: string; n: number }[] = []
    for (let i = MONTHS - 1; i >= 0; i--) {
      const key = monthKey(new Date(now.getFullYear(), now.getMonth() - i, 1).getTime())
      months.push({ key, n: net.get(key) ?? 0 })
    }
    // 最近「所持中」にしたカード（いまも持っているものだけ、同じカードは 1 回）
    const seen = new Set<string>()
    const recent = []
    for (let i = history.length - 1; i >= 0 && recent.length < 30; i--) {
      const h = history[i]
      const c = cardById.get(h.cardId)
      if (h.to !== '所持中' || !c || c.status !== '所持中' || seen.has(c.id)) continue
      seen.add(c.id)
      recent.push({ at: h.changedAt, c, col: colName.get(c.collectionId) ?? '' })
    }
    const owned = data.cards.filter((c) => c.status === '所持中' && (!member || c.memberIds.includes(member))).length
    return { months, recent, owned, first: history[0]?.changedAt }
  }, [data, member])

  if (!view) return <MiniveLoading />
  const { months, recent, owned, first } = view
  const sel = months.find((m) => m.key === picked) ?? months[months.length - 1]
  const m = member ? MEMBER_BY_ID[member] : null

  return (
    <div className="page">
      <TopBar title="集めた記録" back menu />
      <div className="chips" style={{ marginBottom: 12 }}>
        <button className={`chip${!member ? ' on' : ''}`} onClick={() => setMember(null)}>
          全員
        </button>
        {MEMBERS.map((mm) => {
          const on = member === mm.id
          return (
            <button
              key={mm.id}
              className="chip"
              style={on ? { background: mm.color, borderColor: mm.color, color: mm.on } : { color: mm.text }}
              onClick={() => setMember(on ? null : mm.id)}
            >
              {mm.name}
            </button>
          )
        })}
      </div>

      {/* 大きな数字：選んだ月（はじめは今月）に増えた枚数 */}
      <div className="panel">
        <div className="small muted">{monthLabel(sel.key)}に増えたカード{m ? `（${m.name}）` : ''}</div>
        <div className="history-hero num">
          {sel.n > 0 ? '+' : ''}
          {sel.n}
          <span className="history-unit">枚</span>
        </div>
        <MonthChart months={months} selected={sel.key} onPick={setPicked} />
        <div className="xs muted" style={{ marginTop: 6 }}>
          持っているカード <span className="num">{owned}</span> 枚
          {first ? `（記録は ${monthLabel(monthKey(first))}から）` : ''}
        </div>
      </div>

      <div className="section-title">月ごとの枚数</div>
      <table className="history-table">
        <thead>
          <tr>
            <th scope="col">月</th>
            <th scope="col">増えた枚数</th>
          </tr>
        </thead>
        <tbody>
          {[...months].reverse().map((mo) => (
            <tr key={mo.key} className={mo.key === sel.key ? 'on' : undefined} onClick={() => setPicked(mo.key)}>
              <td>{monthLabel(mo.key)}</td>
              <td className="num">
                {mo.n > 0 ? '+' : ''}
                {mo.n} 枚
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="section-title">最近「所持中」にしたカード</div>
      {recent.length === 0 ? (
        <div className="small muted">まだ記録がありません</div>
      ) : (
        <div>
          {recent.map(({ at, c, col }) => (
            <div key={c.id} className="list-item" style={{ minHeight: 0, padding: '8px 0' }}>
              <span className="small muted num" style={{ width: 40, flex: 'none' }}>
                {dayLabel(at)}
              </span>
              <span className="small" style={{ flex: 1, minWidth: 0 }}>
                <span style={{ fontWeight: 700 }}>{memberLabel(c.memberIds)}</span> {[c.source, c.version].filter(Boolean).join(' ')}
                <br />
                <span className="muted xs">{col}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/** 月ごとの棒グラフ（1 色。選んだ月だけ濃く、数字を上に出す）。減った月は線より下に出す */
function MonthChart({ months, selected, onPick }: { months: { key: string; n: number }[]; selected: string; onPick: (key: string) => void }) {
  const W = 340
  const H = 150
  const top = 18 // 数字の分
  const bottom = 20 // 月の文字の分
  const max = Math.max(1, ...months.map((m) => m.n))
  const min = Math.min(0, ...months.map((m) => m.n))
  const plot = H - top - bottom
  const y = (v: number) => top + ((max - v) / (max - min)) * plot
  const slot = W / months.length
  const bw = Math.min(18, slot - 6)
  const r = 4
  return (
    <svg className="history-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="月ごとに増えたカードの枚数（下の表と同じ内容）">
      <line x1={0} x2={W} y1={y(0)} y2={y(0)} className="history-base" />
      {months.map((mo, i) => {
        const x = i * slot + (slot - bw) / 2
        const on = mo.key === selected
        const y0 = y(0)
        const yv = y(mo.n)
        const h = Math.abs(y0 - yv)
        // 0 から伸びる側の端だけを丸める
        const rr = Math.min(r, h / 2, bw / 2)
        const path =
          mo.n >= 0
            ? `M${x},${y0} V${yv + rr} Q${x},${yv} ${x + rr},${yv} H${x + bw - rr} Q${x + bw},${yv} ${x + bw},${yv + rr} V${y0} Z`
            : `M${x},${y0} V${yv - rr} Q${x},${yv} ${x + rr},${yv} H${x + bw - rr} Q${x + bw},${yv} ${x + bw},${yv - rr} V${y0} Z`
        const month = Number(mo.key.slice(5))
        return (
          <g key={mo.key} onClick={() => onPick(mo.key)} style={{ cursor: 'pointer' }}>
            {/* 押しやすいよう、棒より広い透明の当たり */}
            <rect x={i * slot} y={0} width={slot} height={H} fill="transparent" />
            {mo.n !== 0 && <path d={path} className={on ? 'history-bar on' : 'history-bar'} />}
            {on && (
              <text x={x + bw / 2} y={mo.n >= 0 ? yv - 5 : yv + 12} textAnchor="middle" className="history-val">
                {mo.n > 0 ? '+' : ''}
                {mo.n}
              </text>
            )}
            <text x={x + bw / 2} y={H - 5} textAnchor="middle" className={on ? 'history-month on' : 'history-month'}>
              {month === 1 ? `${mo.key.slice(2, 4)}/1` : month}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
