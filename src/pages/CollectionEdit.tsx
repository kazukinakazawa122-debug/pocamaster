import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { IconPhoto } from '@tabler/icons-react'
import { addImages, COLLECTION_TYPES, db, deleteCollection, deleteImages, getThumb, newId, type Collection, type CollectionType } from '../lib/db'
import { makeImage } from '../lib/image'
import { TopBar } from '../components/ui'

/** S-06 コレクションの追加・編集 */
export default function CollectionEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [original, setOriginal] = useState<Collection>()
  const [name, setName] = useState('')
  const [type, setType] = useState<CollectionType>('アルバム（韓国盤）')
  const [releaseDate, setReleaseDate] = useState('')
  const [cover, setCover] = useState<File>()
  const [coverUrl, setCoverUrl] = useState<string>()
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  // 保存の途中で、もう一度押されても 2 回作らない（state は描き直すまで変わらないので、ほぼ同時に 2 回押すと 2 つできていた。2026-10-14）
  const busy = useRef(false)
  const fileRef = useRef<HTMLInputElement>(null)
  // 作った仮の URL は、画面を閉じるときに手放す（開くたびに増えていくため）
  const urls = useRef<string[]>([])
  useEffect(() => () => urls.current.forEach((u) => URL.revokeObjectURL(u)), [])

  useEffect(() => {
    if (!id) return
    db.collections.get(id).then(async (c) => {
      if (!c) return
      setOriginal(c)
      setName(c.name)
      setType(c.type)
      setReleaseDate(c.releaseDate)
      if (c.coverImageId) {
        const thumb = await getThumb(c.coverImageId)
        if (thumb) {
          const u = URL.createObjectURL(thumb)
          urls.current.push(u)
          setCoverUrl(u)
        }
      }
    })
  }, [id])

  const save = async () => {
    if (!name.trim()) {
      setError('名前を入力してください')
      return
    }
    if (busy.current) return
    busy.current = true
    setSaving(true)
    // うまくいかなかったら、理由を出して、もう一度押せるようにする（前は失敗すると「保存中」のまま押せなくなった）
    const fail = (message: string) => {
      busy.current = false
      setSaving(false)
      setError(message)
    }
    let data: Collection
    try {
      const dup = await db.collections.filter((c) => c.name === name.trim() && c.id !== id).count()
      if (dup > 0) return fail('同じ名前のコレクションがすでにあります')
      // 写真を縮めるのは、保存のまとまりの外で（中で待つと、まとまりが先に閉じてしまう）
      const img = cover ? await makeImage(cover) : undefined
      const oldCover = original?.coverImageId
      const coverImageId = img ? newId() : oldCover
      // 編集のときは、元の項目（「ホームに出す」の pinned、初期データの固定の ID の seedId など）を残す。作り直した値だけで上書きすると消える
      data = {
        ...original,
        id: original?.id ?? newId(),
        name: name.trim(),
        type,
        releaseDate,
        coverImageId,
        createdAt: original?.createdAt ?? Date.now(),
      }
      // 新しい表紙の保存・コレクションの保存・古い表紙の削除を 1 回で（途中で失敗しても、表紙のない画像を指したままにしない）
      await db.transaction('rw', db.images, db.thumbs, db.collections, async () => {
        if (img) await addImages([{ id: coverImageId!, ...img }])
        await db.collections.put(data)
        if (img && oldCover) await deleteImages([oldCover])
      })
    } catch (e) {
      return fail(`保存できませんでした：${(e as Error).message}`)
    }
    if (original) navigate(-1)
    else navigate(`/collections/${data.id}`, { replace: true })
  }

  const remove = async () => {
    if (!original) return
    const count = await db.cards.where('collectionId').equals(original.id).count()
    if (!confirm(`「${original.name}」とカード ${count} 枚を削除しますか？元に戻せません。`)) return
    await deleteCollection(original)
    navigate('/collections', { replace: true })
  }

  return (
    <div className="page">
      <TopBar title={original ? 'コレクションを編集' : 'コレクションを追加'} back />

      <label className="field">
        <span>名前</span>
        <input type="text" value={name} onChange={(e) => (setName(e.target.value), setError(''))} placeholder="I've IVE" />
      </label>
      {error && <div className="error">{error}</div>}
      <label className="field">
        <span>種別</span>
        <select value={type} onChange={(e) => setType(e.target.value as CollectionType)}>
          {COLLECTION_TYPES.map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
      </label>
      <label className="field">
        <span>発売日・開催日</span>
        <input type="date" value={releaseDate} onChange={(e) => setReleaseDate(e.target.value)} />
      </label>
      <div className="field">
        <span>カバー画像</span>
        <button type="button" className="cover" style={{ width: 120, height: 120, border: 'none' }} onClick={() => fileRef.current?.click()}>
          {coverUrl ? <img src={coverUrl} alt="" /> : <IconPhoto size={32} aria-label="カバー画像を選ぶ" />}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (!f) return
            setCover(f)
            const u = URL.createObjectURL(f)
            urls.current.push(u)
            setCoverUrl(u)
          }}
        />
      </div>

      <div className="stack" style={{ marginTop: 24 }}>
        <button className="btn primary block" disabled={saving} onClick={save}>
          保存
        </button>
        {original && (
          <button className="btn danger block" onClick={remove}>
            コレクションを削除
          </button>
        )}
      </div>
    </div>
  )
}
