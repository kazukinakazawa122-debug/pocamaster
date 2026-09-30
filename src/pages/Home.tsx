import { useState, useSyncExternalStore } from 'react'
import { liveQuery } from 'dexie'
import { Link } from 'react-router-dom'
import { IconAlertTriangle, IconCrown, IconPhoto } from '@tabler/icons-react'
import { db, getSetting, type Card, type Collection, type Profile } from '../lib/db'
import { MEMBERS, MEMBER_BY_ID, memberLabel, type MemberId } from '../lib/members'
import { isComplete, memberProgress, pctText, progress, type Progress } from '../lib/stats'
import { ProfileAvatar, ProgressBar, useImageUrl } from '../components/ui'
import { cardColors } from '../components/CardTile'
import { MiniveTrio, MiniveLoading } from '../components/Minive'

const BACKUP_REMIND_DAYS = 14

type HomeData = {
  collections: Collection[]
  cards: Card[]
  lastBackupAt?: number
  profile?: Profile
  history: { cardId: string; changedAt: number }[]
}
async function loadHome(): Promise<HomeData> {
  const [collections, cards, lastBackupAt, profile, history] = await Promise.all([
    db.collections.toArray(),
    db.cards.toArray(),
    getSetting<number>('lastBackupAt'),
    getSetting<Profile>('profile'),
    // 最近「所持中」にした記録（同じカードを何度も切り替えることがあるので多めに取る）
    db.statusHistory.orderBy('changedAt').reverse().filter((h) => h.to === '所持中').limit(200).toArray(),
  ])
  return { collections, cards, lastBackupAt, profile, history }
}

// ホームのデータ。ほかの画面から戻ったとき待たせないよう、前回の内容をとっておいてすぐ出す。
// 最新に保つ（カードが変わるたびに読み直す）のは、ホームを開いている間だけ。
// いつも読み直すと、コレクションでカードを切り替えるたびに約 6,000 枚を読み直して遅くなる（本人の報告、2026-09-30）
let lastData: HomeData | undefined
const listeners = new Set<() => void>()
let sub: { unsubscribe(): void } | undefined
let stopTimer: number | undefined
function subscribe(l: () => void) {
  listeners.add(l)
  window.clearTimeout(stopTimer)
  sub ??= liveQuery(loadHome).subscribe({
    next: (v) => {
      lastData = v
      listeners.forEach((f) => f())
    },
  })
  return () => {
    listeners.delete(l)
    // 画面を離れたら読み直しをやめる（すぐ戻ってきたときのために少しだけ待つ）
    stopTimer = window.setTimeout(() => {
      if (listeners.size === 0) {
        sub?.unsubscribe()
        sub = undefined
      }
    }, 300)
  }
}
// アプリを開いたらすぐ 1 回だけ読んでおく（最初にホームを開いたとき待たせないため）
loadHome().then((v) => {
  lastData ??= v
  listeners.forEach((f) => f())
})

const MEMBER_KEY = 'homeMember'
function loadMember(): MemberId | 'all' {
  try {
    const v = localStorage.getItem(MEMBER_KEY)
    return v && v in MEMBER_BY_ID ? (v as MemberId) : 'all'
  } catch {
    return 'all'
  }
}

export default function Home() {
  const data = useSyncExternalStore(subscribe, () => lastData)
  // 選んでいるメンバー（本人の要望、2026-10-01）。「すべて」か 1 人。次に開いたときも同じにする
  const [member, setMemberState] = useState<MemberId | 'all'>(loadMember)
  const setMember = (m: MemberId | 'all') => {
    setMemberState(m)
    try {
      localStorage.setItem(MEMBER_KEY, m)
    } catch {
      /* 保存できなくても表示は変える */
    }
  }
  if (!data) return <MiniveLoading />
  const { collections, lastBackupAt, profile, history = [] } = data
  // メンバーを選んでいるときは、そのメンバーが写っているカード（ソロ・ユニット両方）だけで数える
  const allCards = data.cards
  const cards = member === 'all' ? allCards : allCards.filter((c) => c.memberIds.includes(member))
  const sel = member === 'all' ? null : MEMBER_BY_ID[member]

  // 上のバー：左にプロフィールのアイコン（押すと設定のプロフィールへ）、真ん中にアプリの名前
  const header = (
    <>
      <header className="topbar home">
        <div className="side">
          <Link to="/settings" aria-label="プロフィール">
            <ProfileAvatar profile={profile} size={44} />
          </Link>
        </div>
        <h1 aria-label="pocamaster">
          <MiniveTrio side="left" />
          <span className="wordmark" aria-hidden>
            <span className="wm-poca">poca</span>
            <span className="wm-master">MASTER</span>
            <span className="wm-star">✦</span>
          </span>
          <MiniveTrio side="right" />
        </h1>
      </header>
      <div className="topbar-space" />
      {/* タイトルバーの下にメンバーを選ぶボタン。スクロールしても見える */}
      <div className="chips sticky-chips">
        <button className={`chip${member === 'all' ? ' on' : ''}`} onClick={() => setMember('all')}>
          すべて
        </button>
        {MEMBERS.map((m) => (
          <button
            key={m.id}
            className={`chip member${member === m.id ? ' on' : ''}`}
            style={member === m.id ? { background: m.color, borderColor: m.color, color: m.on } : { color: m.text }}
            onClick={() => setMember(m.id)}
          >
            {m.name}
          </button>
        ))}
      </div>
    </>
  )

  if (collections.length === 0) {
    return (
      <div className="page">
        {header}
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

  // 最近入手したカード：いまも所持中のものだけ、新しい順に 15 枚
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

  // 収集中のアルバム（コレクションの画面で「ホームに出す」を押したもの）。発売日の新しい順
  const pinned = collections
    .filter((c) => c.pinned)
    .sort((a, b) => b.releaseDate.localeCompare(a.releaseDate))
    .map((col) => ({ col, p: progress(byCollection.get(col.id) ?? []) }))
    // メンバーを選んでいるときは、そのメンバーのカードがないコレクションは出さない
    .filter(({ p }) => p.total > 0)
  // お気に入りのカード（コレクションの並び順）
  const favorites = cards.filter((c) => c.favorite).sort((a, b) => a.order - b.order)

  const needBackup =
    cards.length > 0 && (!lastBackupAt || Date.now() - lastBackupAt > BACKUP_REMIND_DAYS * 24 * 60 * 60 * 1000)

  return (
    <div className="page">
      {header}
      {needBackup && (
        <Link to="/settings" className="banner">
          <IconAlertTriangle size={18} aria-hidden />
          {lastBackupAt
            ? `最後のバックアップから ${BACKUP_REMIND_DAYS} 日以上たちました`
            : 'まだバックアップを取っていません'}
        </Link>
      )}

      <div className="section-title">収集中のアルバム</div>
      {pinned.length > 0 ? (
        <div className="h-scroll">
          {pinned.map(({ col, p }) => (
            <PinnedAlbum key={col.id} col={col} p={p} />
          ))}
        </div>
      ) : (
        <div className="xs muted">コレクションの画面で「ホームに出す」を押すと、ここに出ます</div>
      )}

      <div className="section-title">お気に入りのカード</div>
      {favorites.length > 0 ? (
        <div className="h-scroll">
          {favorites.map((card) => (
            <RecentCard key={card.id} card={card} col={colById.get(card.collectionId)} />
          ))}
        </div>
      ) : (
        <div className="xs muted">カードを長押しして ♡ を押すと、ここに出ます</div>
      )}

      {recent.length > 0 && (
        <>
          <div className="section-title">最近入手したカード</div>
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

      {/* 全体コンプ率とメンバー別は下の方に（本人の要望、2026-10-01） */}
      <div className="total-title" style={sel ? { color: sel.text } : undefined}>{sel ? `${sel.name}のコンプ率` : '全体コンプ率'}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span className="total-pct" style={sel ? { color: sel.color } : undefined}>
          {total.pct === null ? '—' : total.pct}
          {total.pct !== null && <span className="pct-sign">%</span>}
        </span>
        <span className="small muted">
          {total.owned} / {total.total} 種類
        </span>
      </div>
      <div style={{ margin: '8px 0' }}>
        <ProgressBar pct={total.pct} color={sel?.color} />
      </div>
      <div className="small muted">
        コンプ済みコレクション <span className="num">{completed.length} / {collections.length}</span>
      </div>

      {/* 全体コンプ率のすぐ下にメンバー別（「すべて」のときだけ。押すとそのメンバーを選ぶ） */}
      {!sel && (
      <>
      <div className="section-title">メンバー別</div>
      <div className="stack">
        {MEMBERS.map((m) => {
          const p = memberProgress(allCards, m.id)
          return (
            <button key={m.id} onClick={() => setMember(m.id)} style={{ display: 'flex', alignItems: 'center', gap: 10, border: 'none', background: 'none', padding: 0, width: '100%', textAlign: 'left' }}>
              <span className="small" style={{ width: 76, color: m.text, fontWeight: 700 }}>
                {m.name}
              </span>
              <div style={{ flex: 1 }}>
                <ProgressBar pct={p.pct} color={m.color} />
              </div>
              <span className="member-pct" style={{ width: 44, textAlign: 'right' }}>
                {pctText(p)}
              </span>
            </button>
          )
        })}
      </div>
      </>
      )}

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

function PinnedAlbum({ col, p }: { col: Collection; p: Progress }) {
  const url = useImageUrl(col.coverImageId, 'thumb')
  return (
    <Link to={`/collections/${col.id}`} style={{ width: 128, flex: 'none' }}>
      <div className="cover" style={{ width: 128, height: 128, position: 'relative' }}>
        {url ? <img src={url} alt="" /> : <IconPhoto size={32} aria-hidden />}
        {isComplete(p) && <IconCrown size={22} color="#D4A017" aria-label="コンプリート" style={{ position: 'absolute', top: 4, right: 4 }} />}
      </div>
      <div className="small" style={{ marginTop: 4, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {col.name}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ flex: 1 }}>
          <ProgressBar pct={p.pct} />
        </div>
        <span className="xs num">{pctText(p)}</span>
      </div>
    </Link>
  )
}

/** 横に並べる小さなカード。at があれば下に日付を出す */
function RecentCard({ card, col, at }: { card: Card; col?: Collection; at?: number }) {
  const url = useImageUrl(card.imageId, 'thumb')
  const { border, background } = cardColors(card)
  const d = at ? new Date(at) : null
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
      {d && (
        <div className="xs muted num" style={{ marginTop: 4, textAlign: 'center' }}>
          {d.getMonth() + 1}/{d.getDate()}
        </div>
      )}
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
