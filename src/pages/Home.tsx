import { useLiveQuery } from 'dexie-react-hooks'
import { Link } from 'react-router-dom'
import { IconAlertTriangle, IconCrown, IconPhoto } from '@tabler/icons-react'
import { db, getSetting, type Card, type Collection } from '../lib/db'
import { MEMBERS, memberLabel } from '../lib/members'
import { isComplete, memberProgress, pctText, progress, type Progress } from '../lib/stats'
import { ProgressBar, useImageUrl } from '../components/ui'
import { cardColors } from '../components/CardTile'

const BACKUP_REMIND_DAYS = 14

export default function Home() {
  const data = useLiveQuery(async () => {
    const [collections, cards, lastBackupAt, history] = await Promise.all([
      db.collections.toArray(),
      db.cards.toArray(),
      getSetting<number>('lastBackupAt'),
      // 最近「所持中」にした記録（同じカードを何度も切り替えることがあるので多めに取る）
      db.statusHistory.orderBy('changedAt').reverse().filter((h) => h.to === '所持中').limit(200).toArray(),
    ])
    return { collections, cards, lastBackupAt, history }
  })
  if (!data) return <div className="page empty">読み込み中…</div>
  const { collections, cards, lastBackupAt, history = [] } = data

  if (collections.length === 0) {
    return (
      <div className="page">
        <div className="empty">
          <p>最初のコレクションを追加しましょう</p>
          <p className="small">設定から初期データを取り込むか、コレクションを追加してください。</p>
          <div className="stack" style={{ maxWidth: 280, margin: '16px auto 0' }}>
            <Link className="btn primary" to="/settings">
              初期データを取り込む
            </Link>
            <Link className="btn" to="/collections/new">
              コレクションを追加
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const total = progress(cards)
  const byCollection = new Map<string, Card[]>()
  for (const c of cards) {
    const list = byCollection.get(c.collectionId)
    if (list) list.push(c)
    else byCollection.set(c.collectionId, [c])
  }
  const completed = collections
    .filter((col) => isComplete(progress(byCollection.get(col.id) ?? [])))
    .map((col) => ({ col, at: Math.max(...(byCollection.get(col.id) ?? []).map((c) => c.statusChangedAt)) }))
    .sort((a, b) => b.at - a.at)

  // 最近ゲットしたカード：いまも所持中のものだけ、新しい順に 15 枚
  const cardById = new Map(cards.map((c) => [c.id, c]))
  const seen = new Set<string>()
  const recent: { card: Card; at: number }[] = []
  for (const h of history) {
    const card = cardById.get(h.cardId)
    if (!card || card.status !== '所持中' || seen.has(card.id)) continue
    seen.add(card.id)
    recent.push({ card, at: h.changedAt })
    if (recent.length >= 15) break
  }

  // もうすぐコンプ：1 枚以上持っていて、まだコンプしていないコレクションを、コンプ率の高い順に 3 つ
  const almost = collections
    .map((col) => ({ col, p: progress(byCollection.get(col.id) ?? []) }))
    .filter(({ p }) => p.owned > 0 && p.owned < p.total)
    .sort((a, b) => b.p.owned / b.p.total - a.p.owned / a.p.total || a.p.total - a.p.owned - (b.p.total - b.p.owned))
    .slice(0, 3)
  const colById = new Map(collections.map((c) => [c.id, c]))

  const needBackup =
    cards.length > 0 && (!lastBackupAt || Date.now() - lastBackupAt > BACKUP_REMIND_DAYS * 24 * 60 * 60 * 1000)

  return (
    <div className="page">
      {needBackup && (
        <Link to="/settings" className="banner">
          <IconAlertTriangle size={18} aria-hidden />
          {lastBackupAt
            ? `最後のバックアップから ${BACKUP_REMIND_DAYS} 日以上たちました`
            : 'まだバックアップを取っていません'}
        </Link>
      )}

      <div className="small muted">全体コンプ率</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span className="num" style={{ fontSize: 44, fontWeight: 500, lineHeight: 1.1 }}>
          {pctText(total)}
        </span>
        <span className="small muted num">
          {total.owned} / {total.total} 種類
        </span>
      </div>
      <div style={{ margin: '8px 0' }}>
        <ProgressBar pct={total.pct} />
      </div>
      <div className="small muted">
        コンプ済みコレクション <span className="num">{completed.length} / {collections.length}</span>
      </div>

      {recent.length > 0 && (
        <>
          <div className="section-title">最近ゲットしたカード</div>
          <div className="h-scroll">
            {recent.map(({ card, at }) => (
              <RecentCard key={card.id} card={card} col={colById.get(card.collectionId)} at={at} />
            ))}
          </div>
        </>
      )}

      {almost.length > 0 && (
        <>
          <div className="section-title">もうすぐコンプ</div>
          {almost.map(({ col, p }) => (
            <AlmostRow key={col.id} col={col} p={p} />
          ))}
        </>
      )}

      <div className="section-title">メンバー別</div>
      <div className="stack">
        {MEMBERS.map((m) => {
          const p = memberProgress(cards, m.id)
          return (
            <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="small" style={{ width: 76, color: m.text, fontWeight: 700 }}>
                {m.name}
              </span>
              <div style={{ flex: 1 }}>
                <ProgressBar pct={p.pct} color={m.color} />
              </div>
              <span className="small num" style={{ width: 40, textAlign: 'right' }}>
                {pctText(p)}
              </span>
            </div>
          )
        })}
      </div>

      {completed.length > 0 && (
        <>
          <div className="section-title">最近コンプしたコレクション</div>
          <div style={{ display: 'flex', gap: 8, overflowX: 'auto' }}>
            {completed.slice(0, 10).map(({ col }) => (
              <CompletedCover key={col.id} col={col} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function RecentCard({ card, col, at }: { card: Card; col?: Collection; at: number }) {
  const url = useImageUrl(card.imageId, 'thumb')
  const { border, background } = cardColors(card)
  const d = new Date(at)
  return (
    <Link to={`/collections/${card.collectionId}`} style={{ width: 72, flex: 'none' }} aria-label={`${col?.name ?? ''} ${memberLabel(card.memberIds)}`}>
      <div className="poca" style={{ borderColor: border, background }}>
        {url ? (
          <img src={url} alt="" decoding="async" />
        ) : (
          <span className="ph">
            <span className="ph-name">{memberLabel(card.memberIds)}</span>
          </span>
        )}
      </div>
      <div className="xs muted num" style={{ marginTop: 4, textAlign: 'center' }}>
        {d.getMonth() + 1}/{d.getDate()}
      </div>
    </Link>
  )
}

function AlmostRow({ col, p }: { col: Collection; p: Progress }) {
  const url = useImageUrl(col.coverImageId, 'thumb')
  return (
    <Link to={`/collections/${col.id}`} className="list-item">
      <div className="cover" style={{ width: 52, height: 52 }}>
        {url ? <img src={url} alt="" /> : <IconPhoto size={22} aria-hidden />}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{col.name}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
          <div style={{ flex: 1 }}>
            <ProgressBar pct={p.pct} />
          </div>
          <span className="small num">{pctText(p)}</span>
        </div>
        <div className="xs muted">あと {p.total - p.owned} 枚</div>
      </div>
    </Link>
  )
}

function CompletedCover({ col }: { col: Collection }) {
  const url = useImageUrl(col.coverImageId, 'thumb')
  return (
    <Link to={`/collections/${col.id}`} style={{ width: 96, flex: 'none' }}>
      <div className="cover" style={{ width: 96, height: 96, position: 'relative' }}>
        {url ? <img src={url} alt="" /> : <IconCrown size={28} aria-hidden />}
      </div>
      <div className="xs" style={{ marginTop: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {col.name}
      </div>
    </Link>
  )
}
