import JSZip from 'jszip'
import { db, putSetting } from './db'

const FORMAT = 1

export async function exportBackup(): Promise<File> {
  const zip = new JSZip()
  const [collections, cards, statusHistory, achievements, settings, images] = await Promise.all([
    db.collections.toArray(),
    db.cards.toArray(),
    db.statusHistory.toArray(),
    db.achievements.toArray(),
    db.settings.toArray(),
    db.images.toArray(),
  ])
  zip.file('data.json', JSON.stringify({ format: FORMAT, exportedAt: Date.now(), collections, cards, statusHistory, achievements, settings }))
  const dir = zip.folder('images')!
  for (const img of images) {
    dir.file(`${img.id}.full.jpg`, img.full)
    dir.file(`${img.id}.thumb.jpg`, img.thumb)
  }
  const blob = await zip.generateAsync({ type: 'blob' })
  const d = new Date()
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
  await putSetting('lastBackupAt', Date.now())
  return new File([blob], `pocamaster-backup-${stamp}.zip`, { type: 'application/zip' })
}

/** iPhone では共有シート（「ファイルに保存」）を使い、使えなければダウンロードする */
export async function saveFile(file: File): Promise<void> {
  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file] })
      return
    } catch (e) {
      if ((e as Error).name === 'AbortError') throw e
    }
  }
  const url = URL.createObjectURL(file)
  const a = document.createElement('a')
  a.href = url
  a.download = file.name
  a.click()
  setTimeout(() => URL.revokeObjectURL(url), 10_000)
}

/** 今のデータをすべて置き換える */
export async function restoreBackup(file: Blob): Promise<void> {
  const zip = await JSZip.loadAsync(file)
  const json = await zip.file('data.json')?.async('string')
  if (!json) throw new Error('バックアップファイルではありません')
  const data = JSON.parse(json)
  if (data.format !== FORMAT) throw new Error('このバックアップの形式には対応していません')

  const images: { id: string; full: Blob; thumb: Blob }[] = []
  const ids = new Set<string>()
  zip.folder('images')!.forEach((path) => ids.add(path.split('.')[0]))
  for (const id of ids) {
    const full = await zip.file(`images/${id}.full.jpg`)?.async('blob')
    const thumb = await zip.file(`images/${id}.thumb.jpg`)?.async('blob')
    if (full && thumb) images.push({ id, full: new Blob([full], { type: 'image/jpeg' }), thumb: new Blob([thumb], { type: 'image/jpeg' }) })
  }

  await db.transaction('rw', [db.collections, db.cards, db.images, db.statusHistory, db.achievements, db.settings], async () => {
    await Promise.all([db.collections.clear(), db.cards.clear(), db.images.clear(), db.statusHistory.clear(), db.achievements.clear(), db.settings.clear()])
    await db.collections.bulkAdd(data.collections)
    await db.cards.bulkAdd(data.cards)
    await db.images.bulkAdd(images)
    await db.statusHistory.bulkAdd(data.statusHistory)
    await db.achievements.bulkAdd(data.achievements)
    await db.settings.bulkAdd(data.settings)
    // data.json は書き出し日を記録する前に作られるため、ここで書き出し日を入れ直す
    await db.settings.put({ key: 'lastBackupAt', value: data.exportedAt })
  })
}
