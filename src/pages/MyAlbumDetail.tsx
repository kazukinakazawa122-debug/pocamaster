import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { IconChevronLeft, IconChevronRight, IconEdit, IconPlus, IconReplace, IconTrash, IconX } from '@tabler/icons-react'
import { ALBUM_PAGE_SIZE, db, type Card, type MyAlbum } from '../lib/db'
import { memberLabel } from '../lib/members'
import { cardColors } from '../components/CardTile'
import CardPicker from '../components/CardPicker'
import { Sheet, TopBar, useImageUrl } from '../components/ui'

/** バインダーのポケット 1 つ。カードがなければ点線の空きポケット */
export function AlbumPocket({ card, onClick, size = 'thumb' }: { card?: Card; onClick?: () => void; size?: 'thumb' | 'full' }) {
  const url = useImageUrl(card?.imageId, size)
  const Tag = onClick ? 'button' : 'div'
  if (!card) {
    return (
      <Tag type={onClick ? 'button' : undefined} className="pocket empty-pocket" onClick={onClick} aria-label={onClick ? 'カードを入れる' : undefined}>
        {onClick && <IconPlus size={22} aria-hidden />}
      </Tag>
    )
  }
  const { border, background } = cardColors(card)
  return (
    <Tag type={onClick ? 'button' : undefined} className="pocket" onClick={onClick} aria-label={onClick ? memberLabel(card.memberIds) : undefined}>
      {/* あとで未所持に戻したカードは暗くする（入れられるのは所持中のカードだけ） */}
      <span className={`poca${card.status === '所持中' ? '' : ' off'}`} style={{ borderColor: border, background }}>
        {url ? (
          <img src={url} alt="" decoding="async" />
        ) : (
          <span className="ph">
            <span className="ph-name">{memberLabel(card.memberIds)}</span>
            <span className="xs">{card.source}</span>
          </span>
        )}
      </span>
    </Tag>
  )
}

/** マイアルバムの中身：3×3 のページを左右にめくる */
export default function MyAlbumDetail({ albumId: id }: { albumId: string }) {
  const [page, setPage] = useState(0)
  const [picking, setPicking] = useState<number | null>(null) // カードを入れるポケットの番号
  const [selected, setSelected] = useState<number | null>(null) // カードの入ったポケットを押したとき
  const [editing, setEditing] = useState(false)
  const [pending, setPending] = useState<number | null>(null) // 足したページ（描き終わってからめくる）
  const pagesRef = useRef<HTMLDivElement>(null)

  const data = useLiveQuery(async () => {
    const album = await db.myAlbums.get(id)
    if (!album) return { album: undefined, cardById: new Map<string, Card>(), colName: new Map<string, string>() }
    const cards = (await db.cards.bulkGet(album.slots.filter((s): s is string => !!s))).filter((c): c is Card => !!c)
    const cols = await db.collections.bulkGet([...new Set(cards.map((c) => c.collectionId))])
    return {
      album,
      cardById: new Map(cards.map((c) => [c.id, c])),
      colName: new Map(cols.filter((c) => !!c).map((c) => [c!.id, c!.name])),
    }
  }, [id])

  const pageCount = data?.album ? Math.max(1, Math.ceil(data.album.slots.length / ALBUM_PAGE_SIZE)) : 1

  const goTo = (p: number) => {
    const el = pagesRef.current
    if (!el) return
    el.scrollTo({ left: p * el.clientWidth })
    setPage(p)
  }

  useLayoutEffect(() => {
    if (pending !== null && pending < pageCount) {
      goTo(pending)
      setPending(null)
    }
  })

  // ページを減らしたときに、いまのページがはみ出さないようにする
  useEffect(() => {
    if (pending === null && page > pageCount - 1) goTo(pageCount - 1)
  })

  if (!data) return <div className="page empty">読み込み中…</div>
  const { album, cardById, colName } = data
  if (!album) return <div className="page empty">アルバムが見つかりません</div>

  const save = (slots: (string | null)[]) => db.myAlbums.update(album.id, { slots })
  const setSlot = (i: number, cardId: string | null) => {
    const slots = [...album.slots]
    slots[i] = cardId
    save(slots)
  }

  const addPage = async () => {
    setPending(pageCount)
    await save([...album.slots, ...Array(ALBUM_PAGE_SIZE).fill(null)])
  }

  const removePage = () => {
    const start = page * ALBUM_PAGE_SIZE
    const inPage = album.slots.slice(start, start + ALBUM_PAGE_SIZE).filter(Boolean).length
    if (inPage > 0 && !confirm(`このページのカード ${inPage} 枚を外して、ページを削除しますか？`)) return
    const slots = [...album.slots.slice(0, start), ...album.slots.slice(start + ALBUM_PAGE_SIZE)]
    save(slots.length ? slots : Array(ALBUM_PAGE_SIZE).fill(null))
  }

  const selCard = selected !== null ? cardById.get(album.slots[selected] ?? '') : undefined

  return (
    <div className="page">
      <TopBar title={album.name} minive>
        <button className="icon-btn" aria-label="アルバムの名前を変える" onClick={() => setEditing(true)}>
          <IconEdit size={22} />
        </button>
      </TopBar>

      <div
        ref={pagesRef}
        className="album-pages"
        onScroll={(e) => {
          const el = e.currentTarget
          const p = Math.round(el.scrollLeft / el.clientWidth)
          if (p !== page) setPage(p)
        }}
      >
        {Array.from({ length: pageCount }, (_, p) => (
          <div key={p} className="album-page">
            <div className="binder">
              {Array.from({ length: ALBUM_PAGE_SIZE }, (_, k) => {
                const i = p * ALBUM_PAGE_SIZE + k
                const cardId = album.slots[i] ?? null
                const card = cardId ? cardById.get(cardId) : undefined
                return <AlbumPocket key={k} card={card} size="full" onClick={() => (card ? setSelected(i) : setPicking(i))} />
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="album-nav">
        <button className="icon-btn" aria-label="前のページ" disabled={page === 0} onClick={() => goTo(page - 1)}>
          <IconChevronLeft size={24} />
        </button>
        <span className="num small">
          {page + 1} / {pageCount}
        </span>
        <button className="icon-btn" aria-label="次のページ" disabled={page >= pageCount - 1} onClick={() => goTo(page + 1)}>
          <IconChevronRight size={24} />
        </button>
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <button className="btn" style={{ flex: 1 }} onClick={addPage}>
          <IconPlus size={20} aria-hidden />
          ページを追加
        </button>
        {pageCount > 1 && (
          <button className="btn danger" style={{ flex: 1 }} onClick={removePage}>
            <IconTrash size={20} aria-hidden />
            このページを削除
          </button>
        )}
      </div>

      {picking !== null && (
        <CardPicker
          onClose={() => setPicking(null)}
          onPick={(c) => {
            setSlot(picking, c.id)
            setPicking(null)
          }}
        />
      )}

      {selected !== null && selCard && (
        <Sheet onClose={() => setSelected(null)}>
          <div style={{ width: 36, height: 5, borderRadius: 3, background: 'var(--line)', margin: '0 auto 12px' }} />
          <div style={{ width: 'min(55vw, 240px)', margin: '0 auto' }}>
            <AlbumPocket card={selCard} size="full" />
          </div>
          <div style={{ textAlign: 'center', margin: '12px 0 16px' }}>
            <div style={{ fontWeight: 700 }}>{memberLabel(selCard.memberIds)}</div>
            <div className="small muted">
              {colName.get(selCard.collectionId)}　{selCard.source} {selCard.version}
            </div>
          </div>
          <div className="stack">
            <button
              className="btn primary block"
              onClick={() => {
                setPicking(selected)
                setSelected(null)
              }}
            >
              <IconReplace size={20} aria-hidden />
              ほかのカードに入れ替える
            </button>
            <button
              className="btn block"
              onClick={() => {
                setSlot(selected, null)
                setSelected(null)
              }}
            >
              <IconX size={20} aria-hidden />
              アルバムから外す
            </button>
          </div>
        </Sheet>
      )}

      {editing && <EditSheet album={album} onClose={() => setEditing(false)} />}
    </div>
  )
}

function EditSheet({ album, onClose }: { album: MyAlbum; onClose: () => void }) {
  const [name, setName] = useState(album.name)
  return (
    <Sheet onClose={onClose}>
      <div style={{ width: 36, height: 5, borderRadius: 3, background: 'var(--line)', margin: '0 auto 12px' }} />
      <label className="field">
        <span>アルバムの名前</span>
        <input type="text" value={name} maxLength={30} onChange={(e) => setName(e.target.value)} />
      </label>
      <button
        className="btn primary block"
        disabled={!name.trim()}
        onClick={async () => {
          await db.myAlbums.update(album.id, { name: name.trim() })
          onClose()
        }}
      >
        保存
      </button>
    </Sheet>
  )
}
