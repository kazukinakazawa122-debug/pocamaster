import JSZip from 'jszip'
import { db, getFull, getSetting, getThumb, putSetting } from './db'
import { memberNames } from './members'

/** 自分でアプリから登録した（切り取った）画像があるカード。ZIP から取り込んだ画像（出典あり）は含まない */
export async function listOwnImageCards() {
  return (await db.cards.toArray()).filter((c) => c.imageId && !c.imageCredit)
}

const EXPORTED_KEY = 'ownExportedImageIds'

/** 前に書き出した（「ファイルに保存する」まで終えた）画像の id。切り直した画像は新しい id なので、また書き出し対象になる */
async function exportedIds(): Promise<Set<string>> {
  return new Set((await getSetting<string[]>(EXPORTED_KEY)) ?? [])
}

/** まだ書き出していない自分の画像があるカード（新しく切り取った・切り直した画像。2026-10-04、本人「毎回同じものを書き出している」） */
export async function listUnexportedOwnImageCards() {
  const done = await exportedIds()
  return (await listOwnImageCards()).filter((c) => !done.has(c.imageId!))
}

/** 保存まで終えた画像を「書き出し済み」にする（保存をやめたときは呼ばない） */
export async function markExported(imageIds: string[]): Promise<void> {
  if (imageIds.length === 0) return
  const done = await exportedIds()
  imageIds.forEach((id) => done.add(id))
  await putSetting(EXPORTED_KEY, [...done])
}

export const OWN_IMAGE_CREDIT = 'アプリで登録'

/**
 * 自分でアプリから登録した画像を、画像の ZIP と同じ形（manifest.json ＋ 画像）で書き出す（2026-10-03、アプリの改善 44.【2】）。
 * パソコンの pocamaster-images に置いて tools/crop/import_app_images.py → merge.py をすると、全部入りの画像 ZIP に入る
 * （アプリを入れ直しても、切り取った画像が残る）。画像の ZIP と同じ形なので、そのままアプリの「画像をまとめて取り込む」でも読める
 */
export async function exportOwnImages(opts: { all?: boolean } = {}): Promise<{ file: File; count: number; skipped: number; imageIds: string[] } | null> {
  // ふつうは、まだ書き出していない画像だけ。all なら、前に書き出した分も入れる（ZIP をなくしたときなど）
  const [cards, collections] = await Promise.all([opts.all ? listOwnImageCards() : listUnexportedOwnImageCards(), db.collections.toArray()])
  if (cards.length === 0) return null
  const colName = new Map(collections.map((c) => [c.id, c.name]))
  const zip = new JSZip()
  const manifest: Record<string, unknown>[] = []
  const imageIds: string[] = []
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
      imageIds.push(c.imageId!)
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
  return { file: new File([blob], `pocamaster-own-images-${stamp}.zip`, { type: 'application/zip' }), count: manifest.length, skipped, imageIds }
}
