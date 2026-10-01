import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { db, newId, type Card } from '../lib/db'
import type { MemberId } from '../lib/members'
import MemberPicker from '../components/MemberPicker'
import { TopBar } from '../components/ui'

/** S-05 カードの編集・追加 */
export default function CardEdit() {
  const { id: collectionIdParam, cardId } = useParams()
  const navigate = useNavigate()
  const [original, setOriginal] = useState<Card>()
  const [collectionId, setCollectionId] = useState(collectionIdParam ?? '')
  const [memberIds, setMemberIds] = useState<MemberId[]>([])
  const [source, setSource] = useState('')
  const [version, setVersion] = useState('')
  const [sources, setSources] = useState<string[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    if (!cardId) return
    db.cards.get(cardId).then((c) => {
      if (!c) return
      setOriginal(c)
      setCollectionId(c.collectionId)
      setMemberIds(c.memberIds)
      setSource(c.source)
      setVersion(c.version)
    })
  }, [cardId])

  // そのコレクションで使ったことのある入手元を候補に出す
  useEffect(() => {
    if (!collectionId) return
    db.cards
      .where('collectionId')
      .equals(collectionId)
      .toArray()
      .then((cards) => setSources([...new Set(cards.map((c) => c.source))]))
  }, [collectionId])

  const save = async () => {
    if (memberIds.length === 0) return setError('メンバーを 1 人以上選んでください')
    if (!source.trim()) return setError('入手元を入力してください')
    if (original) {
      await db.cards.update(original.id, { memberIds, source: source.trim(), version: version.trim() })
    } else {
      const last = await db.cards.where('collectionId').equals(collectionId).sortBy('order')
      await db.cards.add({
        id: newId(),
        collectionId,
        memberIds,
        source: source.trim(),
        version: version.trim(),
        status: '未所持',
        statusChangedAt: Date.now(),
        order: (last.at(-1)?.order ?? -1) + 1,
      })
    }
    navigate(-1)
  }

  return (
    <div className="page">
      <TopBar title={original ? 'カードを編集' : 'カードを追加'} back />
      <div className="field">
        <span>メンバー（ユニットは複数選ぶ）</span>
        <MemberPicker value={memberIds} onChange={(v) => (setMemberIds(v), setError(''))} />
      </div>
      <label className="field">
        <span>入手元</span>
        <input type="text" list="sources" value={source} onChange={(e) => (setSource(e.target.value), setError(''))} placeholder="Soundwave 特典" />
        <datalist id="sources">
          {sources.map((s) => (
            <option key={s} value={s} />
          ))}
        </datalist>
      </label>
      <label className="field">
        <span>バージョン（なければ空欄）</span>
        <input type="text" value={version} onChange={(e) => setVersion(e.target.value)} placeholder="ver.1" />
      </label>
      {error && <div className="error">{error}</div>}
      <button className="btn primary block" onClick={save}>
        保存
      </button>
    </div>
  )
}
