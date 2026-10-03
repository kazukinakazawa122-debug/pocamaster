import JSZip from 'jszip'
import { db, type Card, type Collection } from '../lib/db'
import { reloadCards } from '../lib/cardStore'

/** 全部の表を空にする（テストごとに初期状態から始める） */
export async function resetDb(): Promise<void> {
  // 6,000 枚を 1 表ずつ clear すると fake-indexeddb では遅い（10 秒を超える）ので、データベースごと作り直す
  db.close()
  await db.delete()
  await db.open()
  await reloadCards()
}

export const jpeg = (text: string) => new Blob([text], { type: 'image/jpeg' })

export function collection(over: Partial<Collection> = {}): Collection {
  return { id: 'col1', name: 'テスト盤', type: 'アルバム（韓国盤）', releaseDate: '2026-01-01', createdAt: 1, ...over }
}

export function card(over: Partial<Card> = {}): Card {
  return { id: 'c1', collectionId: 'col1', memberIds: ['yujin'], source: '本体封入', version: 'A', status: '未所持', statusChangedAt: 1, order: 0, ...over }
}

/** 画像の ZIP（manifest.json ＋ 画像。一覧用の画像も付ける＝縮める処理を使わない）を作る */
export async function imageZip(
  entries: { collection: string; members: string[]; source: string; version: string; credit?: string; cover?: boolean }[],
  info?: object,
): Promise<Blob> {
  const zip = new JSZip()
  const manifest = entries.map((e, i) => {
    zip.file(`img/${i}.jpg`, `full-${i}`)
    zip.file(`img/${i}_t.jpg`, `thumb-${i}`)
    return { ...e, file: `img/${i}.jpg`, thumb: `img/${i}_t.jpg` }
  })
  zip.file('manifest.json', JSON.stringify(manifest))
  if (info) zip.file('info.json', JSON.stringify(info))
  return zip.generateAsync({ type: 'blob' })
}
