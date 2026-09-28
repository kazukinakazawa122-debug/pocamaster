import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { IconEdit, IconPhotoPlus, IconTrash } from '@tabler/icons-react'
import { db, deleteCard, newId, type Card } from '../lib/db'
import { makeImage } from '../lib/image'
import { memberLabel } from '../lib/members'
import { cardColors } from './CardTile'
import { Sheet, useImageUrl } from './ui'

interface Props {
  card: Card
  collectionName: string
  onClose: () => void
  onToggle: () => void
}

/** S-04 カード拡大 */
export default function CardSheet({ card, collectionName, onClose, onToggle }: Props) {
  const url = useImageUrl(card.imageId, 'full')
  const fileRef = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const { border, background } = cardColors(card)
  const owned = card.status === '所持中'

  const onFile = async (file: File | undefined) => {
    if (!file) return
    setBusy(true)
    setError('')
    try {
      const img = await makeImage(file)
      const id = newId()
      await db.transaction('rw', db.images, db.cards, async () => {
        await db.images.add({ id, ...img })
        await db.cards.update(card.id, { imageId: id, imageCredit: undefined })
        if (card.imageId) await db.images.delete(card.imageId)
      })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    if (!confirm('このカードを削除しますか？元に戻せません。')) return
    await deleteCard(card)
    onClose()
  }

  return (
    <Sheet onClose={onClose}>
      <div style={{ width: 36, height: 5, borderRadius: 3, background: 'var(--line)', margin: '0 auto 12px' }} />
      <div
        className={`poca${owned ? '' : ' off'}`}
        style={{ borderColor: border, background, width: 'min(70vw, 300px)', margin: '0 auto' }}
      >
        {url ? (
          <img src={url} alt="" />
        ) : (
          <span className="ph" style={{ gap: 4 }}>
            <span className="small muted">{collectionName}</span>
            <span style={{ fontSize: 20, fontWeight: 700 }}>{memberLabel(card.memberIds)}</span>
            <span>{card.source}</span>
            {card.version && <span className="muted">{card.version}</span>}
          </span>
        )}
      </div>

      <div style={{ textAlign: 'center', margin: '12px 0 16px' }}>
        <div style={{ fontWeight: 700 }}>{memberLabel(card.memberIds)}</div>
        <div className="small muted">
          {collectionName}　{card.source} {card.version}
        </div>
        {card.imageId && card.imageCredit && <div className="xs muted">画像：{card.imageCredit}</div>}
      </div>

      <div className="stack">
        <button className="btn primary block" onClick={onToggle}>
          {owned ? '未所持にする' : '所持中にする'}
        </button>
        <button className="btn block" disabled={busy} onClick={() => fileRef.current?.click()}>
          <IconPhotoPlus size={20} aria-hidden />
          {busy ? '保存中…' : card.imageId ? '画像を変更' : '画像を登録'}
        </button>
        <input ref={fileRef} type="file" accept="image/*" hidden onChange={(e) => onFile(e.target.files?.[0])} />
        {error && <div className="error" style={{ margin: 0 }}>{error}</div>}
        <div style={{ display: 'flex', gap: 8 }}>
          <Link className="btn" style={{ flex: 1 }} to={`/cards/${card.id}/edit`}>
            <IconEdit size={20} aria-hidden />
            編集
          </Link>
          <button className="btn danger" style={{ flex: 1 }} onClick={remove}>
            <IconTrash size={20} aria-hidden />
            削除
          </button>
        </div>
      </div>
    </Sheet>
  )
}
