import { beforeEach, describe, expect, it } from 'vitest'
import collectionsCsv from '../../public/seed/collections.csv?raw'
import cardsCsv from '../../public/seed/cards.csv?raw'
import removedCsv from '../../public/seed/removed.csv?raw'
import { db, setCardStatus } from './db'
import { importCsv, parseCsv, parseMembers, removeObsolete } from './csv'
import { resetDb } from '../test/helpers'

const rows = (text: string) => {
  const [head, ...body] = parseCsv(text).filter((r) => r.length > 1 || r[0])
  return body.map((r) => Object.fromEntries(head.map((h, i) => [h.trim(), (r[i] ?? '').trim()])))
}

const slotKey = (r: Record<string, string>) => `${r.collection}|${r.member}|${r.source}|${r.version ?? ''}`

/** 初期データ（public/seed）の形の確認。ここが壊れると、アプリに入れ直したときに大量の記録がずれる */
describe('初期データ（public/seed）', () => {
  const cols = rows(collectionsCsv)
  const cards = rows(cardsCsv)

  it('すべての枠のコレクションが collections.csv にあり、メンバー名が読める', () => {
    const names = new Set(cols.map((c) => c.name))
    expect(names.size).toBe(cols.length) // コレクション名は重ならない
    for (const c of cards) {
      expect(names.has(c.collection), `コレクション「${c.collection}」がない`).toBe(true)
      expect(() => parseMembers(c.member), `メンバー「${c.member}」`).not.toThrow()
    }
  })

  it('同じ枠（コレクション・メンバー・入手元・バージョン）が重ならない', () => {
    const seen = new Set<string>()
    const dup: string[] = []
    for (const c of cards) {
      const key = [c.collection, [...parseMembers(c.member)].sort().join('+'), c.source, c.version ?? ''].join('|')
      if (seen.has(key)) dup.push(key)
      seen.add(key)
    }
    expect(dup).toEqual([])
  })

  it('消す一覧（removed.csv）の枠が、いまの初期データ（cards.csv）にまだ残っていない', () => {
    const now = new Set(cards.map(slotKey))
    const still = rows(removedCsv).filter((r) => now.has(slotKey(r)))
    expect(still.map(slotKey)).toEqual([])
  })
})

describe('初期データの取り込み', () => {
  beforeEach(resetDb)

  it('全部入る。2 回目はすべて「すでにある」で、増えない', async () => {
    const r1 = await importCsv(collectionsCsv, cardsCsv)
    expect(r1.addedCards).toBe(rows(cardsCsv).length)
    expect(r1.skippedCards).toBe(0)
    const r2 = await importCsv(collectionsCsv, cardsCsv)
    expect(r2.addedCollections).toBe(0)
    expect(r2.addedCards).toBe(0)
    expect(r2.skippedCards).toBe(r1.addedCards)
    expect(await db.cards.count()).toBe(r1.addedCards)
  }, 60_000)

  it('取り込み直しで、持っている記録・お気に入りを上書きしない', async () => {
    await importCsv(collectionsCsv, cardsCsv)
    const target = (await db.cards.toArray())[0]
    await setCardStatus(target, '所持中')
    await db.cards.update(target.id, { favorite: true })
    await importCsv(collectionsCsv, cardsCsv)
    const after = (await db.cards.get(target.id))!
    expect(after.status).toBe('所持中')
    expect(after.favorite).toBe(true)
  }, 60_000)

  it('まちがえた枠（removed.csv）は消すが、持っている・お気に入りの枠は消さない', async () => {
    // 消す一覧の先頭 3 つの枠を、古い版で作った枠のつもりでアプリに作る
    const targets = rows(removedCsv).slice(0, 3)
    for (const [i, r] of targets.entries()) {
      let c = (await db.collections.toArray()).find((x) => x.name === r.collection)
      if (!c) {
        c = { id: `col-${i}`, name: r.collection, type: 'その他', releaseDate: '', createdAt: 1 }
        await db.collections.add(c)
      }
      await db.cards.add({ id: `x${i}`, collectionId: c.id, memberIds: parseMembers(r.member), source: r.source, version: r.version ?? '', status: '未所持', statusChangedAt: 1, order: i })
    }
    await setCardStatus((await db.cards.get('x0'))!, '所持中') // 持っている
    await db.cards.update('x1', { favorite: true }) // お気に入り
    const n = await removeObsolete(removedCsv)
    expect(n).toBe(1) // 消えるのは x2 だけ
    expect(await db.cards.get('x0')).toBeTruthy()
    expect(await db.cards.get('x1')).toBeTruthy()
    expect(await db.cards.get('x2')).toBeUndefined()
  }, 60_000)
})
