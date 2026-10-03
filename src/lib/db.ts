import Dexie, { type EntityTable } from 'dexie'
import type { MemberId } from './members'

export const COLLECTION_TYPES = [
  'アルバム（韓国盤）',
  'アルバム（日本盤）',
  'シーズングリーティング',
  'ファンミ・ファンコン',
  'ライブ・ツアー',
  'ノンアルバム',
  '個人（ソロ）',
  'ポップアップ',
  'その他',
] as const
export type CollectionType = (typeof COLLECTION_TYPES)[number]

export type CardStatus = '未所持' | '所持中'

export interface Collection {
  id: string
  /** 初期データ（collections.csv の id 列）の固定の ID。名前が変わっても同じコレクションとわかる（2026-10-03） */
  seedId?: string
  name: string
  type: CollectionType
  releaseDate: string // YYYY-MM-DD
  coverImageId?: string
  /** ホームの「集め中のアルバム」に出す */
  pinned?: boolean
  createdAt: number
}

export interface Card {
  id: string
  /** 初期データ（cards.csv の id 列）の固定の ID。名前・番号を直しても同じ枠とわかる。自分で作ったカードにはない（2026-10-03） */
  seedId?: string
  collectionId: string
  memberIds: MemberId[]
  source: string
  version: string
  imageId?: string
  /** 画像の出典（一覧表の作者など） */
  imageCredit?: string
  /** 画像 ZIP から取り込んだ画像の指紋（SHA-1）。同じ画像の取り込み直しをとばし、途中で止まった取り込みを続きから行うため（2026-10-03） */
  imageHash?: string
  /** お気に入り（ホームに出す） */
  favorite?: boolean
  /** 譲れる（交換に出せる重なったカード。「譲」の一覧に出す。2026-10-01） */
  trade?: boolean
  status: CardStatus
  statusChangedAt: number
  order: number
}

export interface StoredImage {
  id: string
  full: Blob
  /** 版 4 より前に保存した画像だけが持つ。いまの一覧用の小さい画像は thumbs に分けて保存する */
  thumb?: Blob
}

/** 一覧用の小さい画像（id は images と同じ） */
export interface StoredThumb {
  id: string
  thumb: Blob
}

export interface StatusHistory {
  id?: number
  cardId: string
  from: CardStatus
  to: CardStatus
  changedAt: number
}

export interface Achievement {
  key: string
  unlockedAt: number
}

/** 1 ページのポケットの数（3×3） */
export const ALBUM_PAGE_SIZE = 9

/** マイアルバム：自分で好きなカードを並べるバインダー。slots はページ順に 9 個ずつ並べたカードの id（空きは null） */
export interface MyAlbum {
  id: string
  name: string
  slots: (string | null)[]
  createdAt: number
}

/** 自分のプロフィール（settings の 'profile' に保存） */
export interface Profile {
  name: string
  /** 推しメン */
  biasIds: MemberId[]
  /** ひとこと */
  bio: string
  /** アイコンの画像（images の id） */
  imageId?: string
}

export const EMPTY_PROFILE: Profile = { name: '', biasIds: [], bio: '' }

export interface Setting {
  key: string
  value: unknown
}

export const db = new Dexie('pocamaster') as Dexie & {
  collections: EntityTable<Collection, 'id'>
  cards: EntityTable<Card, 'id'>
  images: EntityTable<StoredImage, 'id'>
  thumbs: EntityTable<StoredThumb, 'id'>
  statusHistory: EntityTable<StatusHistory, 'id'>
  achievements: EntityTable<Achievement, 'key'>
  settings: EntityTable<Setting, 'key'>
  myAlbums: EntityTable<MyAlbum, 'id'>
}

db.version(1).stores({
  collections: 'id, type, releaseDate',
  cards: 'id, collectionId, *memberIds, status',
  images: 'id',
  statusHistory: '++id, cardId, changedAt',
  achievements: 'key',
  settings: 'key',
})

// 種別「ファンミ・コンサート」を「ファンミ・ファンコン」と「ライブ・ツアー」に分けた
db.version(2)
  .stores({})
  .upgrade((tx) =>
    tx
      .table('collections')
      .toCollection()
      .modify((c: Collection) => {
        if ((c.type as string) !== 'ファンミ・コンサート') return
        c.type = /TOUR|ツアー|ライブ|LIVE/i.test(c.name) ? 'ライブ・ツアー' : 'ファンミ・ファンコン'
      }),
  )

// マイアルバムを追加（実績の画面の代わり、2026-09-30）
db.version(3).stores({ myAlbums: 'id, createdAt' })

// 一覧用の小さい画像を別の表に分けた（一覧で大きい画像を読まないため、2026-10-01）。
// 前に保存した画像は移さない（iPhone で数千枚を一度に書き換えないため）。画像の ZIP を取り込み直すと分かれる
db.version(4).stores({ thumbs: 'id' })

/** 画像を保存する。一覧用の小さい画像は thumbs に分ける */
export async function addImages(list: { id: string; full: Blob; thumb: Blob }[]): Promise<void> {
  if (list.length === 0) return
  await db.transaction('rw', db.images, db.thumbs, async () => {
    await db.images.bulkAdd(list.map(({ id, full }) => ({ id, full })))
    await db.thumbs.bulkAdd(list.map(({ id, thumb }) => ({ id, thumb })))
  })
}

export async function deleteImages(ids: string[]): Promise<void> {
  if (ids.length === 0) return
  await db.transaction('rw', db.images, db.thumbs, async () => {
    await db.images.bulkDelete(ids)
    await db.thumbs.bulkDelete(ids)
  })
}

/** 一覧用の小さい画像。分ける前に保存した画像は images の中のものを使う */
export async function getThumb(id: string): Promise<Blob | undefined> {
  return (await db.thumbs.get(id))?.thumb ?? (await db.images.get(id))?.thumb
}

export async function getFull(id: string): Promise<Blob | undefined> {
  return (await db.images.get(id))?.full
}

export async function createMyAlbum(name: string): Promise<string> {
  const id = newId()
  await db.myAlbums.add({ id, name, slots: Array(ALBUM_PAGE_SIZE).fill(null), createdAt: Date.now() })
  return id
}

export function newId(): string {
  return crypto.randomUUID()
}

export async function setCardStatus(card: Card, to: CardStatus): Promise<void> {
  if (card.status === to) return
  const now = Date.now()
  await db.transaction('rw', db.cards, db.statusHistory, async () => {
    await db.cards.update(card.id, { status: to, statusChangedAt: now })
    await db.statusHistory.add({ cardId: card.id, from: card.status, to, changedAt: now })
  })
}

/** 何枚かの状態をまとめて変える（1 回の保存。すでにその状態のカードは変えない） */
export async function setCardsStatus(cards: Card[], to: CardStatus): Promise<void> {
  const change = cards.filter((c) => c.status !== to)
  if (change.length === 0) return
  const now = Date.now()
  await db.transaction('rw', db.cards, db.statusHistory, async () => {
    await db.cards.bulkUpdate(change.map((c) => ({ key: c.id, changes: { status: to, statusChangedAt: now } })))
    await db.statusHistory.bulkAdd(change.map((c) => ({ cardId: c.id, from: c.status, to, changedAt: now })))
  })
}

/** 何枚かを、それぞれ前の状態に戻す（まとめて変えたあとの「元に戻す」） */
export async function restoreCardsStatus(cards: Card[], now: CardStatus): Promise<void> {
  const t = Date.now()
  const change = cards.filter((c) => c.status !== now)
  await db.transaction('rw', db.cards, db.statusHistory, async () => {
    await db.cards.bulkUpdate(change.map((c) => ({ key: c.id, changes: { status: c.status, statusChangedAt: c.statusChangedAt } })))
    await db.statusHistory.bulkAdd(change.map((c) => ({ cardId: c.id, from: now, to: c.status, changedAt: t })))
  })
}

export async function deleteCard(card: Card): Promise<void> {
  await deleteCards([card])
}

/**
 * カードをまとめて消す（1 回の保存でまとめて行うので、数百枚でも速い）。
 * 画像・記録を消し、マイアルバムに入れていたらそのポケットを空ける
 */
export async function deleteCards(cards: Card[]): Promise<void> {
  if (cards.length === 0) return
  const ids = cards.map((c) => c.id)
  const gone = new Set(ids)
  const imageIds = cards.flatMap((c) => (c.imageId ? [c.imageId] : []))
  await db.transaction('rw', [db.cards, db.images, db.thumbs, db.statusHistory, db.myAlbums], async () => {
    await deleteImages(imageIds)
    await db.statusHistory.where('cardId').anyOf(ids).delete()
    await db.cards.bulkDelete(ids)
    await db.myAlbums
      .filter((a) => a.slots.some((s) => s !== null && gone.has(s)))
      .modify((a: MyAlbum) => {
        a.slots = a.slots.map((s) => (s !== null && gone.has(s) ? null : s))
      })
  })
}

export async function deleteCollection(c: Collection): Promise<void> {
  const cards = await db.cards.where('collectionId').equals(c.id).toArray()
  await db.transaction('rw', [db.collections, db.cards, db.images, db.thumbs, db.statusHistory, db.myAlbums], async () => {
    await deleteCards(cards)
    if (c.coverImageId) await deleteImages([c.coverImageId])
    await db.collections.delete(c.id)
  })
}

export async function getSetting<T>(key: string): Promise<T | undefined> {
  return (await db.settings.get(key))?.value as T | undefined
}

export async function putSetting(key: string, value: unknown): Promise<void> {
  await db.settings.put({ key, value })
}
