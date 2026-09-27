import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { db, newId, type Card } from '../lib/db'
import { MEMBERS, memberOrder, type MemberId } from '../lib/members'
import MemberPicker from '../components/MemberPicker'
import { TopBar } from '../components/ui'

/** S-07 カードの枠をまとめて作る（メンバー × 入手元 × バージョン） */
export default function BulkCreate() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const [source, setSource] = useState('')
  const [versionsText, setVersionsText] = useState('')
  const [memberIds, setMemberIds] = useState<MemberId[]>(MEMBERS.map((m) => m.id))
  const [asUnit, setAsUnit] = useState(false)
  const [error, setError] = useState('')

  const versions = versionsText
    .split(/[,、，]/)
    .map((v) => v.trim())
    .filter(Boolean)
  const vs = versions.length ? versions : ['']
  const perVersion = asUnit ? 1 : memberIds.length
  const count = perVersion * vs.length

  const create = async () => {
    if (!source.trim()) return setError('入手元を入力してください')
    if (memberIds.length === 0) return setError('メンバーを 1 人以上選んでください')
    const existing = await db.cards.where('collectionId').equals(id).sortBy('order')
    let order = (existing.at(-1)?.order ?? -1) + 1
    const sorted = [...memberIds].sort((a, b) => memberOrder(a) - memberOrder(b))
    const now = Date.now()
    const cards: Card[] = []
    for (const version of vs) {
      const groups = asUnit ? [sorted] : sorted.map((m) => [m])
      for (const g of groups) {
        cards.push({ id: newId(), collectionId: id, memberIds: g, source: source.trim(), version, status: '未所持', statusChangedAt: now, order: order++ })
      }
    }
    await db.cards.bulkAdd(cards)
    navigate(-1)
  }

  return (
    <div className="page">
      <TopBar title="まとめて追加" back />
      <label className="field">
        <span>入手元</span>
        <input type="text" value={source} onChange={(e) => (setSource(e.target.value), setError(''))} placeholder="Soundwave 特典" />
      </label>
      <label className="field">
        <span>バージョン（カンマ区切り。なければ空欄）</span>
        <input type="text" value={versionsText} onChange={(e) => setVersionsText(e.target.value)} placeholder="ver.1, ver.2, ver.3" />
      </label>
      <div className="field">
        <span>メンバー</span>
        <MemberPicker value={memberIds} onChange={(v) => (setMemberIds(v), setError(''))} />
      </div>
      <label style={{ display: 'flex', alignItems: 'center', gap: 8, minHeight: 44, marginBottom: 16 }}>
        <input type="checkbox" checked={asUnit} onChange={(e) => setAsUnit(e.target.checked)} style={{ width: 22, height: 22 }} />
        選んだメンバーで 1 枚のユニットカードにする
      </label>
      {error && <div className="error">{error}</div>}
      <p className="small muted">
        {asUnit ? 'ユニット 1 枚' : `${memberIds.length} 人`} × {vs.length} バージョン ＝ <b className="num">{count}</b> 枚を作ります
      </p>
      <button className="btn primary block" onClick={create} disabled={count === 0}>
        作成
      </button>
    </div>
  )
}
