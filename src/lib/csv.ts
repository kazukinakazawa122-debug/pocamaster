import { db, newId, COLLECTION_TYPES, type Card, type Collection, type CollectionType } from './db'
import { MEMBER_BY_NAME, MEMBERS, type MemberId } from './members'

/** ダブルクォート対応の簡単な CSV パーサー */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = []
  let row: string[] = []
  let cell = ''
  let quoted = false
  const src = text.replace(/^\uFEFF/, '')
  for (let i = 0; i < src.length; i++) {
    const ch = src[i]
    if (quoted) {
      if (ch === '"' && src[i + 1] === '"') {
        cell += '"'
        i++
      } else if (ch === '"') quoted = false
      else cell += ch
    } else if (ch === '"') quoted = true
    else if (ch === ',') {
      row.push(cell)
      cell = ''
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && src[i + 1] === '\n') i++
      row.push(cell)
      rows.push(row)
      row = []
      cell = ''
    } else cell += ch
  }
  if (cell !== '' || row.length > 0) {
    row.push(cell)
    rows.push(row)
  }
  return rows.filter((r) => r.some((c) => c.trim() !== ''))
}

function toObjects(text: string): Record<string, string>[] {
  const [header, ...rows] = parseCsv(text)
  if (!header) return []
  const keys = header.map((h) => h.trim())
  return rows.map((r) => Object.fromEntries(keys.map((k, i) => [k, (r[i] ?? '').trim()])))
}

/** 「ユジン/ウォニョン」「全員」を ID の配列にする */
export function parseMembers(text: string): MemberId[] {
  if (text === '全員') return MEMBERS.map((m) => m.id)
  return text.split(/[/・]/).map((name) => {
    const m = MEMBER_BY_NAME[name.trim()]
    if (!m) throw new Error(`メンバー名がわかりません：「${name}」`)
    return m.id
  })
}

function cardKey(collectionId: string, memberIds: MemberId[], source: string, version: string): string {
  return [collectionId, [...memberIds].sort().join('+'), source, version].join('|')
}

export interface ImportResult {
  addedCollections: number
  addedCards: number
  skippedCards: number
}

/**
 * collections.csv（name,type,releaseDate）と cards.csv（collection,member,source,version）を取り込む。
 * すでにあるコレクション・カードはそのまま（状態を上書きしない）。
 */
export async function importCsv(collectionsCsv: string, cardsCsv: string): Promise<ImportResult> {
  const colRows = toObjects(collectionsCsv)
  const cardRows = toObjects(cardsCsv)
  const result: ImportResult = { addedCollections: 0, addedCards: 0, skippedCards: 0 }

  await db.transaction('rw', db.collections, db.cards, async () => {
    const byName = new Map<string, Collection>((await db.collections.toArray()).map((c) => [c.name, c]))
    const now = Date.now()

    for (const r of colRows) {
      if (!r.name || byName.has(r.name)) continue
      const type = (COLLECTION_TYPES as readonly string[]).includes(r.type) ? (r.type as CollectionType) : 'その他'
      const c: Collection = { id: newId(), name: r.name, type, releaseDate: r.releaseDate ?? '', createdAt: now }
      await db.collections.add(c)
      byName.set(c.name, c)
      result.addedCollections++
    }

    const existing = await db.cards.toArray()
    const keys = new Set(existing.map((c) => cardKey(c.collectionId, c.memberIds, c.source, c.version)))
    const orderBase = new Map<string, number>()
    for (const c of existing) orderBase.set(c.collectionId, Math.max(orderBase.get(c.collectionId) ?? 0, c.order + 1))

    const toAdd: Card[] = []
    cardRows.forEach((r, i) => {
      const col = byName.get(r.collection)
      if (!col) throw new Error(`${i + 2} 行目：コレクション「${r.collection}」が collections.csv にありません`)
      const memberIds = parseMembers(r.member)
      const key = cardKey(col.id, memberIds, r.source, r.version ?? '')
      if (keys.has(key)) {
        result.skippedCards++
        return
      }
      keys.add(key)
      const order = orderBase.get(col.id) ?? 0
      orderBase.set(col.id, order + 1)
      toAdd.push({
        id: newId(),
        collectionId: col.id,
        memberIds,
        source: r.source,
        version: r.version ?? '',
        status: '未所持',
        statusChangedAt: now,
        order,
      })
    })
    await db.cards.bulkAdd(toAdd)
    result.addedCards = toAdd.length
  })
  return result
}
