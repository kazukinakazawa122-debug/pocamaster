import { useEffect, useState } from 'react'
import { createMyAlbum, db } from '../lib/db'
import MyAlbumDetail from './MyAlbumDetail'

/**
 * 下のタブ「マイアルバム」。アルバムは 1 冊だけ（本人の要望、2026-09-30）。
 * 開いたらすぐ 1 ページ目を出す。まだなければ作る
 */
// 同時に 2 回呼ばれても 1 冊しか作らない
let ensuring: Promise<string> | null = null
function ensureAlbum(): Promise<string> {
  ensuring ??= (async () => (await db.myAlbums.orderBy('createdAt').first())?.id ?? (await createMyAlbum('マイアルバム')))().finally(() => {
    ensuring = null
  })
  return ensuring
}

export default function MyAlbums() {
  const [id, setId] = useState<string>()
  useEffect(() => {
    let alive = true
    ensureAlbum().then((albumId) => alive && setId(albumId))
    return () => {
      alive = false
    }
  }, [])
  if (!id) return <div className="page empty">読み込み中…</div>
  return <MyAlbumDetail albumId={id} />
}
