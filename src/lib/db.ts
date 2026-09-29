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
  collectionId: string
  memberIds: MemberId[]
  source: string
  version: string
  imageId?: string
  /** 画像の出典（一覧表の作者など） */
  imageCredit?: string
  /** お気に入り（ホームに出す） */
  favorite?: boolean
  status: CardStatus
  statusChangedAt: number
  order: number
}

export interface StoredImage {
  id: string
  full: Blob
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

export async function deleteCard(card: Card): Promise<void> {
  await db.transaction('rw', [db.cards, db.images, db.statusHistory, db.myAlbums], async () => {
    if (card.imageId) await db.images.delete(card.imageId)
    await db.statusHistory.where('cardId').equals(card.id).delete()
    await db.cards.delete(card.id)
    // マイアルバムに入れていたら、そのポケットを空ける
    await db.myAlbums
      .filter((a) => a.slots.includes(card.id))
      .modify((a: MyAlbum) => {
        a.slots = a.slots.map((s) => (s === card.id ? null : s))
      })
  })
}

export async function deleteCollection(c: Collection): Promise<void> {
  const cards = await db.cards.where('collectionId').equals(c.id).toArray()
  await db.transaction('rw', [db.collections, db.cards, db.images, db.statusHistory, db.myAlbums], async () => {
    for (const card of cards) await deleteCard(card)
    if (c.coverImageId) await db.images.delete(c.coverImageId)
    await db.collections.delete(c.id)
  })
}

export async function getSetting<T>(key: string): Promise<T | undefined> {
  return (await db.settings.get(key))?.value as T | undefined
}

export async function putSetting(key: string, value: unknown): Promise<void> {
  await db.settings.put({ key, value })
}
