import { useLiveQuery } from 'dexie-react-hooks'
import { Link, useNavigate } from 'react-router-dom'
import { IconPlus } from '@tabler/icons-react'
import { ALBUM_PAGE_SIZE, createMyAlbum, db, type Card, type MyAlbum } from '../lib/db'
import { AlbumIcon } from '../components/TabIcons'
import { TopBar } from '../components/ui'
import { AlbumPocket } from './MyAlbumDetail'

/** マイアルバムの一覧（下のタブ「マイアルバム」） */
export default function MyAlbums() {
  const navigate = useNavigate()
  const data = useLiveQuery(async () => {
    const albums = await db.myAlbums.orderBy('createdAt').toArray()
    // 一覧には 1 ページ目だけ小さく出す
    const ids = [...new Set(albums.flatMap((a) => a.slots.slice(0, ALBUM_PAGE_SIZE)).filter((s): s is string => !!s))]
    const cards = (await db.cards.bulkGet(ids)).filter((c): c is Card => !!c)
    return { albums, cardById: new Map(cards.map((c) => [c.id, c])) }
  })

  const create = async () => {
    const n = (data?.albums.length ?? 0) + 1
    const id = await createMyAlbum(`マイアルバム ${n}`)
    navigate(`/albums/${id}`)
  }

  return (
    <div className="page">
      <TopBar title="マイアルバム">
        <button className="icon-btn" aria-label="アルバムを作る" onClick={create}>
          <IconPlus size={22} />
        </button>
      </TopBar>

      {!data ? (
        <div className="empty">読み込み中…</div>
      ) : data.albums.length === 0 ? (
        <div className="empty">
          <AlbumIcon size={48} stroke={1.2} aria-hidden />
          <p>好きなポカを 3×3 のバインダーに並べて、自分だけのアルバムを作れます</p>
          <button className="btn primary" onClick={create}>
            アルバムを作る
          </button>
        </div>
      ) : (
        <div className="album-list">
          {data.albums.map((a) => (
            <AlbumItem key={a.id} album={a} cardById={data.cardById} />
          ))}
        </div>
      )}
    </div>
  )
}

function AlbumItem({ album, cardById }: { album: MyAlbum; cardById: Map<string, Card> }) {
  const pages = Math.max(1, Math.ceil(album.slots.length / ALBUM_PAGE_SIZE))
  const count = album.slots.filter(Boolean).length
  return (
    <Link to={`/albums/${album.id}`} className="album-item">
      <div className="binder binder-mini">
        {album.slots.slice(0, ALBUM_PAGE_SIZE).map((s, i) => (
          <AlbumPocket key={i} card={s ? cardById.get(s) : undefined} />
        ))}
      </div>
      <div style={{ marginTop: 6, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{album.name}</div>
      <div className="xs muted num">
        {pages} ページ・{count} 枚
      </div>
    </Link>
  )
}
