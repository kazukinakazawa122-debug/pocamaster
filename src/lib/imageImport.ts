import JSZip from 'jszip'
import { db, newId, type Card } from './db'
import { makeImage } from './image'
import { parseMembers } from './csv'

interface ManifestEntry {
  collection: string
  members: string[]
  source: string
  version: string
  file: string
  /** 一覧用の小さい画像（あれば縮める処理を省く） */
  thumb?: string
  credit?: string
  /** true ならカードではなく、コレクションの表紙（アルバムのジャケットなど）にする */
  cover?: boolean
}

export interface ImageImportResult {
  matched: number
  unmatched: string[]
}

function cardKey(collectionId: string, memberIds: string[], source: string, version: string): string {
  return [collectionId, [...memberIds].sort().join('+'), source, version].join('|')
}

/**
 * 画像の ZIP（manifest.json ＋ 画像）を取り込み、カードに画像を付ける。
 * コレクション名・メンバー・入手元・バージョンが一致するカードに付け、すでにある画像は置き換える。
 */
export async function importImages(file: Blob, onProgress?: (done: number, total: number) => void): Promise<ImageImportResult> {
  const zip = await JSZip.loadAsync(file)
  const json = await zip.file('manifest.json')?.async('string')
  if (!json) throw new Error('画像の取り込み用ファイルではありません（manifest.json がありません）')
  const entries = JSON.parse(json) as ManifestEntry[]

  const [collections, cards] = await Promise.all([db.collections.toArray(), db.cards.toArray()])
  const colId = new Map(collections.map((c) => [c.name, c.id]))
  const byKey = new Map<string, Card>(cards.map((c) => [cardKey(c.collectionId, c.memberIds, c.source, c.version), c]))

  const result: ImageImportResult = { matched: 0, unmatched: [] }
  // 50 枚ずつまとめて保存する（1 枚ずつより速い）
  let pending: { id: string; card: Card; img: { full: Blob; thumb: Blob }; credit?: string }[] = []
  const flush = async () => {
    const batch = pending
    pending = []
    if (batch.length === 0) return
    await db.transaction('rw', db.images, db.cards, async () => {
      await db.images.bulkAdd(batch.map((b) => ({ id: b.id, ...b.img })))
      for (const b of batch) {
        await db.cards.update(b.card.id, { imageId: b.id, imageCredit: b.credit })
        if (b.card.imageId) await db.images.delete(b.card.imageId)
      }
    })
  }
  for (const [i, e] of entries.entries()) {
    onProgress?.(i, entries.length)
    if (e.cover) {
      // コレクションの表紙：いまの表紙を置き換える
      const col = collections.find((c) => c.name === e.collection)
      const bytes = await zip.file(e.file)?.async('arraybuffer')
      const thumb = e.thumb ? await zip.file(e.thumb)?.async('arraybuffer') : undefined
      if (!col || !bytes) {
        result.unmatched.push(`${e.collection}（表紙）`)
        continue
      }
      const full = new Blob([bytes], { type: 'image/jpeg' })
      const img = thumb ? { full, thumb: new Blob([thumb], { type: 'image/jpeg' }) } : await makeImage(full)
      const id = newId()
      await db.transaction('rw', db.images, db.collections, async () => {
        await db.images.add({ id, ...img })
        await db.collections.update(col.id, { coverImageId: id })
        if (col.coverImageId) await db.images.delete(col.coverImageId)
      })
      result.matched++
      continue
    }
    const label = `${e.collection} / ${e.members.join('・')} / ${e.source} ${e.version}`.trim()
    const cid = colId.get(e.collection)
    const card = cid ? byKey.get(cardKey(cid, parseMembers(e.members.join('/')), e.source, e.version)) : undefined
    // 中身をいったんメモリに読み出してから保存する（元の ZIP ファイルを参照したままだと、
    // iPhone であとから「The I/O read operation failed」で読めなくなることがあるため）
    const bytes = await zip.file(e.file)?.async('arraybuffer')
    const blob = bytes && new Blob([bytes], { type: 'image/jpeg' })
    if (!card || !blob) {
      result.unmatched.push(label)
      continue
    }
    const thumb = e.thumb ? await zip.file(e.thumb)?.async('arraybuffer') : undefined
    const img = thumb ? { full: blob, thumb: new Blob([thumb], { type: 'image/jpeg' }) } : await makeImage(blob)
    const id = newId()
    pending.push({ id, card, img, credit: e.credit })
    if (pending.length >= 50) await flush()
    result.matched++
  }
  await flush()
  onProgress?.(entries.length, entries.length)
  return result
}
