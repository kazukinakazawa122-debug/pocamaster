import { useEffect, useState } from 'react'
import { createMyAlbum, db } from '../lib/db'
import { MiniveLoading } from '../components/Minive'
import MyAlbumDetail from './MyAlbumDetail'

/**
 * 下のタブ「マイアルバム」。アルバムは 1 冊だけ（本人の要望、2026-09-30）。
 * 開いたらすぐ 1 ページ目を出す。まだなければ作る
 */
// 同時に 2 回呼ばれても 1 冊しか作らない
let ensuring: Promise<string> | null = null
function ensureAlbum(): Promise<string> {
  ensuring ??= (async () => {
    const first = await db.myAlbums.orderBy('createdAt').first()
    if (!first) return createMyAlbum('マイアルバム')
    // 前は「マイアルバム 1」のように番号をつけていた（何冊も作れたころ）。1 冊だけになったので番号を外す
    if (/^マイアルバム \d+$/.test(first.name)) await db.myAlbums.update(first.id, { name: 'マイアルバム' })
    return first.id
  })().finally(() => {
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
  if (!id) return <MiniveLoading />
  return <MyAlbumDetail albumId={id} />
}
