import { db, deleteCards, newId, COLLECTION_TYPES, type Card, type Collection, type CollectionType } from './db'
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
  /** すでにあって、変わらない枠 */
  skippedCards: number
  /** 固定の ID で見つけ、新しい名前・番号に直した枠（持っている記録・画像はそのまま） */
  renamedCards: number
  renamedCollections: number
  /** 名前で見つけて、初めて固定の ID を付けた枠 */
  adoptedCards: number
}

/**
 * collections.csv（name,type,releaseDate,id）と cards.csv（collection,member,source,version,id）を取り込む。
 * すでにあるコレクション・カードはそのまま（状態を上書きしない）。
 *
 * id 列（固定の ID）があるときは、まず ID で同じ枠を探す（2026-10-03）。名前・番号が直されていても、持っている記録・画像・お気に入りは引き継がれる
 * （玉突きの付け替え「1→2・2→3」でも、最後の名前を一度に書き込むので重ならない）。ID がまだない枠（これまでに取り込んだ枠）は、名前で見つけて ID を付ける。
 * id 列のない CSV（古い形）は、これまでどおり名前だけで探す
 */
export async function importCsv(collectionsCsv: string, cardsCsv: string): Promise<ImportResult> {
  const colRows = toObjects(collectionsCsv)
  const cardRows = toObjects(cardsCsv)
  const result: ImportResult = { addedCollections: 0, addedCards: 0, skippedCards: 0, renamedCards: 0, renamedCollections: 0, adoptedCards: 0 }
  for (const [what, list] of [['コレクション', colRows], ['カード', cardRows]] as const) {
    const ids = list.map((r) => r.id).filter(Boolean)
    if (new Set(ids).size !== ids.length) throw new Error(`${what}の id が重なっています（初期データが壊れています）`)
  }

  await db.transaction('rw', db.collections, db.cards, async () => {
    const now = Date.now()

    // --- コレクション ---
    const existingCols = await db.collections.toArray()
    const colBySeed = new Map(existingCols.filter((c) => c.seedId).map((c) => [c.seedId!, c]))
    const legacyCols = new Map(existingCols.filter((c) => !c.seedId).map((c) => [c.name, c]))
    const claimedCols = new Set<string>()
    const byName = new Map<string, Collection>()
    const colUpdates: { key: string; changes: Partial<Collection> }[] = []
    for (const r of colRows) {
      if (!r.name) continue
      const bySeed = r.id ? colBySeed.get(r.id) : undefined
      if (bySeed) {
        claimedCols.add(bySeed.id)
        if (bySeed.name !== r.name) {
          colUpdates.push({ key: bySeed.id, changes: { name: r.name } })
          result.renamedCollections++
        }
        byName.set(r.name, { ...bySeed, name: r.name })
        continue
      }
      const legacy = legacyCols.get(r.name)
      if (legacy && !claimedCols.has(legacy.id)) {
        claimedCols.add(legacy.id)
        if (r.id) colUpdates.push({ key: legacy.id, changes: { seedId: r.id } })
        byName.set(r.name, legacy)
        continue
      }
      const type = (COLLECTION_TYPES as readonly string[]).includes(r.type) ? (r.type as CollectionType) : 'その他'
      const c: Collection = { id: newId(), name: r.name, type, releaseDate: r.releaseDate ?? '', createdAt: now, ...(r.id ? { seedId: r.id } : {}) }
      await db.collections.add(c)
      byName.set(c.name, c)
      result.addedCollections++
    }
    // CSV にないコレクション（自分で作ったもの）も、名前で引けるようにしておく
    for (const c of existingCols) if (!claimedCols.has(c.id) && !byName.has(c.name)) byName.set(c.name, c)
    if (colUpdates.length) await db.collections.bulkUpdate(colUpdates)

    // --- カード ---
    const existing = await db.cards.toArray()
    const cardBySeed = new Map(existing.filter((c) => c.seedId).map((c) => [c.seedId!, c]))
    const legacyByKey = new Map<string, Card[]>()
    for (const c of existing) {
      if (c.seedId) continue
      const k = cardKey(c.collectionId, c.memberIds, c.source, c.version)
      legacyByKey.set(k, [...(legacyByKey.get(k) ?? []), c])
    }
    const claimed = new Set<string>()
    const orderBase = new Map<string, number>()
    for (const c of existing) orderBase.set(c.collectionId, Math.max(orderBase.get(c.collectionId) ?? 0, c.order + 1))
    const keys = new Set<string>()

    const updates: { key: string; changes: Partial<Card> }[] = []
    const toAdd: Card[] = []
    cardRows.forEach((r, i) => {
      const col = byName.get(r.collection)
      if (!col) throw new Error(`${i + 2} 行目：コレクション「${r.collection}」が collections.csv にありません`)
      const memberIds = parseMembers(r.member)
      const version = r.version ?? ''
      const key = cardKey(col.id, memberIds, r.source, version)

      // 1. 固定の ID で同じ枠を探す
      const hit = r.id ? cardBySeed.get(r.id) : undefined
      if (hit) {
        claimed.add(hit.id)
        keys.add(key)
        if (cardKey(hit.collectionId, hit.memberIds, hit.source, hit.version) !== key) {
          updates.push({ key: hit.id, changes: { collectionId: col.id, memberIds, source: r.source, version } })
          result.renamedCards++
        } else result.skippedCards++
        return
      }
      // 2. ID のない枠を名前で見つける（初めての ID つなぎ。id 列のない CSV もここ）
      const legacy = legacyByKey.get(key)?.find((c) => !claimed.has(c.id))
      if (legacy) {
        claimed.add(legacy.id)
        keys.add(key)
        if (r.id) {
          updates.push({ key: legacy.id, changes: { seedId: r.id } })
          result.adoptedCards++
        } else result.skippedCards++
        return
      }
      // 3. ない枠は作る
      if (keys.has(key)) {
        result.skippedCards++
        return
      }
      keys.add(key)
      const order = orderBase.get(col.id) ?? 0
      orderBase.set(col.id, order + 1)
      toAdd.push({
        id: newId(),
        ...(r.id ? { seedId: r.id } : {}),
        collectionId: col.id,
        memberIds,
        source: r.source,
        version,
        status: '未所持',
        statusChangedAt: now,
        order,
      })
    })
    if (updates.length) await db.cards.bulkUpdate(updates)
    await db.cards.bulkAdd(toAdd)
    result.addedCards = toAdd.length
  })
  return result
}

/**
 * 初期データからなくした枠（まちがえて作った枠など）を消す。removed.csv（collection,member,source,version）。
 * 所持中・お気に入りにしたカードは消さない。消した枚数を返す
 */
export async function removeObsolete(removedCsv: string, currentCardsCsv = ''): Promise<number> {
  const rows = toObjects(removedCsv)
  if (rows.length === 0) return 0
  // いまの初期データ（cards.csv）にある枠は、消す一覧にまちがって入っていても消さない（番号を付け替えた枠など）
  const current = new Set(currentCardsCsv ? toObjects(currentCardsCsv).map((r) => `${r.collection}|${r.member}|${r.source}|${r.version ?? ''}`) : [])
  const byName = new Map((await db.collections.toArray()).map((c) => [c.name, c]))
  const targets = new Set(
    rows.flatMap((r) => {
      if (current.has(`${r.collection}|${r.member}|${r.source}|${r.version ?? ''}`)) return []
      const col = byName.get(r.collection)
      if (!col) return []
      try {
        return [cardKey(col.id, parseMembers(r.member), r.source, r.version ?? '')]
      } catch {
        // 読めない行が 1 つあっても、ほかの行の削除は続ける
        return []
      }
    }),
  )
  // いまの初期データにある固定の ID の枠は、名前が消す一覧と同じでも消さない（名前を付け替えた枠など）
  const currentIds = new Set(currentCardsCsv ? toObjects(currentCardsCsv).map((r) => r.id).filter(Boolean) : [])
  const cards = (await db.cards.toArray()).filter(
    (c) => targets.has(cardKey(c.collectionId, c.memberIds, c.source, c.version)) && c.status === '未所持' && !c.favorite && !(c.seedId && currentIds.has(c.seedId)),
  )
  await deleteCards(cards)
  return cards.length
}
