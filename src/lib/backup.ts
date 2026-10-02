import JSZip from 'jszip'
import { addImages, db, putSetting, type Profile } from './db'
import { reloadCards } from './cardStore'

const FORMAT = 1

/**
 * バックアップの ZIP を作る。
 * 画像の ZIP から取り込んだ画像（出典のあるもの）は、ZIP を取り込み直せば戻るので入れない。
 * 自分で登録した画像とコレクションの表紙だけを入れる（全部入れると 100MB を超え、iPhone で失敗するため）
 */
export async function exportBackup(): Promise<{ file: File; skipped: number }> {
  const zip = new JSZip()
  const [collections, cards, statusHistory, achievements, settings, myAlbums] = await Promise.all([
    db.collections.toArray(),
    db.cards.toArray(),
    db.statusHistory.toArray(),
    db.achievements.toArray(),
    db.settings.toArray(),
    db.myAlbums.toArray(),
  ])
  zip.file('data.json', JSON.stringify({ format: FORMAT, exportedAt: Date.now(), collections, cards, statusHistory, achievements, settings, myAlbums }))
  const ownIds = [
    ...cards.filter((c) => c.imageId && !c.imageCredit).map((c) => c.imageId!),
    ...collections.filter((c) => c.coverImageId).map((c) => c.coverImageId!),
  ]
  // プロフィールのアイコン
  const profile = settings.find((s) => s.key === 'profile')?.value as Profile | undefined
  if (profile?.imageId) ownIds.push(profile.imageId)
  const dir = zip.folder('images')!
  // 読めない画像（iPhone で「The I/O read operation failed」になるもの）は飛ばし、記録だけでも保存できるようにする
  let skipped = 0
  const [fulls, thumbs] = await Promise.all([db.images.bulkGet(ownIds), db.thumbs.bulkGet(ownIds)])
  for (const [i, img] of fulls.entries()) {
    // 一覧用の小さい画像は thumbs にある（分ける前に保存した画像は images の中）
    const thumbBlob = thumbs[i]?.thumb ?? img?.thumb
    if (!img || !thumbBlob) continue
    try {
      const [full, thumb] = await Promise.all([img.full.arrayBuffer(), thumbBlob.arrayBuffer()])
      dir.file(`${img.id}.full.jpg`, full)
      dir.file(`${img.id}.thumb.jpg`, thumb)
    } catch {
      skipped++
    }
  }
  const blob = await zip.generateAsync({ type: 'blob' })
  const d = new Date()
  const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
  return { file: new File([blob], `pocamaster-backup-${stamp}.zip`, { type: 'application/zip' }), skipped }
}

/** 保存できたら、最後にバックアップした日を記録する */
export async function markBackedUp(): Promise<void> {
  await putSetting('lastBackupAt', Date.now())
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
  zip.folder('images')?.forEach((path) => ids.add(path.split('.')[0]))
  for (const id of ids) {
    const full = await zip.file(`images/${id}.full.jpg`)?.async('arraybuffer')
    const thumb = await zip.file(`images/${id}.thumb.jpg`)?.async('arraybuffer')
    if (full && thumb) images.push({ id, full: new Blob([full], { type: 'image/jpeg' }), thumb: new Blob([thumb], { type: 'image/jpeg' }) })
  }

  // バックアップに入っていない画像（画像の ZIP から取り込んだもの）は、ZIP を取り込み直すまで画像なしにする
  const have = new Set(images.map((i) => i.id))
  for (const c of data.cards) if (c.imageId && !have.has(c.imageId)) delete c.imageId
  for (const c of data.collections) if (c.coverImageId && !have.has(c.coverImageId)) delete c.coverImageId

  await db.transaction('rw', [db.collections, db.cards, db.images, db.thumbs, db.statusHistory, db.achievements, db.settings, db.myAlbums], async () => {
    await Promise.all([
      db.collections.clear(), db.cards.clear(), db.images.clear(), db.thumbs.clear(), db.statusHistory.clear(), db.achievements.clear(), db.settings.clear(), db.myAlbums.clear(),
    ])
    // マイアルバムを作る前のバックアップには myAlbums がない
    await db.myAlbums.bulkAdd(data.myAlbums ?? [])
    await db.collections.bulkAdd(data.collections)
    await db.cards.bulkAdd(data.cards)
    await addImages(images)
    await db.statusHistory.bulkAdd(data.statusHistory)
    await db.achievements.bulkAdd(data.achievements)
    await db.settings.bulkAdd(data.settings)
    // 戻したバックアップの日付を「最後のバックアップ」にする
    await db.settings.put({ key: 'lastBackupAt', value: data.exportedAt })
    // 画像の ZIP から取り込んだ画像は戻らないので、取り込んだ版の記録も消す（全部入りの ZIP から取り込み直す）
    await db.settings.delete('imageZip')
  })
  // 全部が入れ替わったので、手元のカードの記録も読み直す
  await reloadCards()
}
