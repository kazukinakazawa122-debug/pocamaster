import { useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { db, deleteCard, type Card } from '../lib/db'
import { memberLabel } from '../lib/members'
import { candidatesFor, keepAsOwn, listOrphans, mergeCardInto } from '../lib/orphans'
import { TopBar } from '../components/ui'

const label = (c: Card) => `${c.source}${c.version ? ` ${c.version}` : ''}`

/**
 * 初期データにない枠の整理（2026-10-03）。名前・番号を付け替えられて、初期データとつながらなくなった枠や、自分で作ったカードが並ぶ。
 * 初期データの枠へ付け替える（持っている記録・お気に入り・画像を移す）／自分の枠として残す／消す
 */
export default function Orphans() {
  const orphans = useLiveQuery(listOrphans)
  const all = useLiveQuery(() => db.cards.toArray())
  const collections = useLiveQuery(() => db.collections.toArray())
  const [pick, setPick] = useState<Record<string, string>>({})
  const [message, setMessage] = useState('')

  const colName = new Map((collections ?? []).map((c) => [c.id, c.name]))
  const byId = new Map((all ?? []).map((c) => [c.id, c]))
  // 持っているカード・お気に入りなど、記録のある枠を先に（なくしたくないものから見る）
  const rank = (c: Card) => Number(c.status === '所持中') * 4 + Number(!!c.favorite) * 2 + Number(!!c.imageId)
  const sorted = [...(orphans ?? [])].sort((a, b) => rank(b) - rank(a) || (colName.get(a.collectionId) ?? '').localeCompare(colName.get(b.collectionId) ?? ''))

  return (
    <div className="page">
      <TopBar title="初期データにない枠" back />
      <p className="small muted" style={{ marginBottom: 12 }}>
        名前・番号が付け替えられて、初期データとつながらなくなった枠や、自分で作ったカードです。
        初期データの枠へ付け替えると、持っている記録・お気に入り・画像がそちらへ移ります。
      </p>
      {message && (
        <p className="small" role="status" style={{ marginBottom: 12 }}>
          {message}
        </p>
      )}
      {orphans && sorted.length === 0 && <p className="muted">整理する枠はありません。</p>}
      <div className="stack">
        {sorted.map((c) => {
          const cands = candidatesFor(c, all ?? [])
          const target = byId.get(pick[c.id] ?? cands[0]?.id ?? '')
          return (
            <div key={c.id} className="panel stack" data-testid="orphan">
              <div>
                <div style={{ fontWeight: 700 }}>
                  {memberLabel(c.memberIds)}　{label(c)}
                </div>
                <div className="xs muted">
                  {colName.get(c.collectionId)}
                  {c.status === '所持中' ? '　持っている' : ''}
                  {c.favorite ? '　お気に入り' : ''}
                  {c.trade ? '　譲' : ''}
                  {c.imageId ? '　画像あり' : ''}
                </div>
              </div>
              {cands.length > 0 ? (
                <>
                  <label className="field">
                    <select value={target?.id ?? ''} onChange={(e) => setPick({ ...pick, [c.id]: e.target.value })} aria-label="付け替え先の枠">
                      {cands.map((t) => (
                        <option key={t.id} value={t.id}>
                          {label(t)}
                          {t.status === '所持中' ? '（持っている）' : ''}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button
                    className="btn primary block"
                    disabled={!target}
                    onClick={async () => {
                      if (!target) return
                      await mergeCardInto(c, target)
                      setMessage(`「${label(c)}」の記録を「${label(target)}」へ移しました`)
                    }}
                  >
                    この枠へ付け替える
                  </button>
                </>
              ) : (
                <div className="xs muted">付け替えられる初期データの枠が、同じコレクションの同じメンバーにはありません</div>
              )}
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn" onClick={() => keepAsOwn(c)}>
                  自分の枠として残す
                </button>
                <button
                  className="btn"
                  onClick={async () => {
                    if (!confirm(`「${memberLabel(c.memberIds)} ${label(c)}」を消します。よろしいですか？`)) return
                    await deleteCard(c)
                    setMessage('消しました')
                  }}
                >
                  消す
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
