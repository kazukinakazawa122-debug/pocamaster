import { useLiveQuery } from 'dexie-react-hooks'
import { Link } from 'react-router-dom'
import { IconAlertTriangle, IconCrown } from '@tabler/icons-react'
import { db, getSetting, type Card, type Collection } from '../lib/db'
import { MEMBERS } from '../lib/members'
import { isComplete, memberProgress, pctText, progress } from '../lib/stats'
import { ProgressBar, useImageUrl } from '../components/ui'

const BACKUP_REMIND_DAYS = 14

export default function Home() {
  const data = useLiveQuery(async () => {
    const [collections, cards, lastBackupAt] = await Promise.all([
      db.collections.toArray(),
      db.cards.toArray(),
      getSetting<number>('lastBackupAt'),
    ])
    return { collections, cards, lastBackupAt }
  })
  if (!data) return null
  const { collections, cards, lastBackupAt } = data

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
  for (const c of cards) byCollection.set(c.collectionId, [...(byCollection.get(c.collectionId) ?? []), c])
  const completed = collections
    .filter((col) => isComplete(progress(byCollection.get(col.id) ?? [])))
    .map((col) => ({ col, at: Math.max(...(byCollection.get(col.id) ?? []).map((c) => c.statusChangedAt)) }))
    .sort((a, b) => b.at - a.at)
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
