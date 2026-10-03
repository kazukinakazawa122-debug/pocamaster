import JSZip from 'jszip'
import { db, getFull, getThumb } from './db'
import { memberNames } from './members'

/** 自分でアプリから登録した（切り取った）画像があるカード。ZIP から取り込んだ画像（出典あり）は含まない */
export async function listOwnImageCards() {
  return (await db.cards.toArray()).filter((c) => c.imageId && !c.imageCredit)
}

export const OWN_IMAGE_CREDIT = 'アプリで登録'

/**
 * 自分でアプリから登録した画像を、画像の ZIP と同じ形（manifest.json ＋ 画像）で書き出す（2026-10-03、アプリの改善 44.【2】）。
 * パソコンの pocamaster-images に置いて tools/crop/import_app_images.py → merge.py をすると、全部入りの画像 ZIP に入る
 * （アプリを入れ直しても、切り取った画像が残る）。画像の ZIP と同じ形なので、そのままアプリの「画像をまとめて取り込む」でも読める
 */
export async function exportOwnImages(): Promise<{ file: File; count: number; skipped: number } | null> {
  const [cards, collections] = await Promise.all([listOwnImageCards(), db.collections.toArray()])
  if (cards.length === 0) return null
  const colName = new Map(collections.map((c) => [c.id, c.name]))
  const zip = new JSZip()
  const manifest: Record<string, unknown>[] = []
  let skipped = 0
  for (const c of cards) {
    const name = colName.get(c.collectionId)
    try {
      const [full, thumb] = await Promise.all([getFull(c.imageId!), getThumb(c.imageId!)])
      if (!name || !full || !thumb) {
        skipped++
        continue
      }
      const n = String(manifest.length).padStart(4, '0')
      zip.file(`own/${n}.jpg`, await full.arrayBuffer())
      zip.file(`own/${n}_t.jpg`, await thumb.arrayBuffer())
      manifest.push({
        collection: name,
        members: memberNames(c.memberIds),
        source: c.source,
        version: c.version,
        file: `own/${n}.jpg`,
        thumb: `own/${n}_t.jpg`,
        credit: OWN_IMAGE_CREDIT,
        // 名前が変わっても同じ枠とわかるように、固定の ID も付ける（初期データの枠のとき）
        ...(c.seedId ? { seedId: c.seedId } : {}),
      })
    } catch {
      skipped++ // 読めない画像は飛ばす（iPhone の「I/O read operation failed」など）
    }
  }
  if (manifest.length === 0) return null
  zip.file('manifest.json', JSON.stringify(manifest))
  const blob = await zip.generateAsync({ type: 'blob' })
  const d = new Date()
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
  return { file: new File([blob], `pocamaster-own-images-${stamp}.zip`, { type: 'application/zip' }), count: manifest.length, skipped }
}
