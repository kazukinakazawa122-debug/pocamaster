import { beforeEach, describe, expect, it } from 'vitest'
import { db, setCardStatus, type Card } from './db'
import { importCsv, removeObsolete } from './csv'
import { resetDb } from '../test/helpers'

const COLS = 'name,type,releaseDate,id\nアルバム A,アルバム（韓国盤）,2026-01-01,colA\n'
const head = 'collection,member,source,version,id\n'
const cardsCsv = (rows: string[][]) => head + rows.map((r) => r.join(',')).join('\n') + '\n'
const byVersion = async (v: string): Promise<Card | undefined> => (await db.cards.toArray()).find((c) => c.version === v)

/** 枠の固定の ID（名前・番号を直しても同じ枠とわかる）。「持っている」の記録がずれないことを確かめる */
describe('固定の ID での引き継ぎ', () => {
  beforeEach(resetDb)

  it('初めての取り込みで、ID つきの枠が作られる', async () => {
    const r = await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'QQ Music', '1', 's1']]))
    expect(r.addedCards).toBe(1)
    expect((await db.cards.toArray())[0].seedId).toBe('s1')
    expect((await db.collections.toArray())[0].seedId).toBe('colA')
  })

  it('ID のない昔の枠は、名前で見つけて ID を付ける（持っている記録はそのまま）', async () => {
    // ID の列がない古い CSV で取り込んだ状態
    await importCsv('name,type,releaseDate\nアルバム A,アルバム（韓国盤）,2026-01-01\n', 'collection,member,source,version\nアルバム A,ユジン,QQ Music,1\n')
    const before = (await db.cards.toArray())[0]
    expect(before.seedId).toBeUndefined()
    await setCardStatus(before, '所持中')
    // ID つきの CSV を取り込む
    const r = await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'QQ Music', '1', 's1']]))
    expect(r.adoptedCards).toBe(1)
    expect(r.addedCards).toBe(0)
    const after = (await db.cards.toArray())[0]
    expect(after.id).toBe(before.id)
    expect(after.seedId).toBe('s1')
    expect(after.status).toBe('所持中')
    expect((await db.collections.toArray())[0].seedId).toBe('colA')
  })

  it('名前・番号が直されても、同じ枠として引き継ぐ（持っている・お気に入り・画像・id はそのまま）', async () => {
    await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'QQ Music', '1', 's1']]))
    const c = (await db.cards.toArray())[0]
    await setCardStatus(c, '所持中')
    await db.cards.update(c.id, { favorite: true, imageId: 'img1' })
    // 番号を「1」→「Christmas」に直した初期データ
    const r = await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'QQ Music × Starship Square', 'Christmas', 's1']]))
    expect(r.renamedCards).toBe(1)
    expect(r.addedCards).toBe(0)
    expect(await db.cards.count()).toBe(1)
    const after = (await db.cards.get(c.id))!
    expect([after.source, after.version]).toEqual(['QQ Music × Starship Square', 'Christmas'])
    expect([after.status, after.favorite, after.imageId]).toEqual(['所持中', true, 'img1'])
  })

  it('玉突きの付け替え（1→2・2→3・3→1）でも、記録は ID についていく', async () => {
    const rows = (v: [string, string, string]) => cardsCsv([['アルバム A', 'ユジン', 'QQ', v[0], 's1'], ['アルバム A', 'ユジン', 'QQ', v[1], 's2'], ['アルバム A', 'ユジン', 'QQ', v[2], 's3']])
    await importCsv(COLS, rows(['1', '2', '3']))
    const s1 = (await db.cards.toArray()).find((c) => c.seedId === 's1')!
    await setCardStatus(s1, '所持中') // s1 だけ持っている
    const r = await importCsv(COLS, rows(['2', '3', '1'])) // s1 は「2」、s2 は「3」、s3 は「1」になった
    expect(r.renamedCards).toBe(3)
    expect(await db.cards.count()).toBe(3)
    const all = await db.cards.toArray()
    const bySeed = Object.fromEntries(all.map((c) => [c.seedId, c]))
    expect([bySeed.s1.version, bySeed.s2.version, bySeed.s3.version]).toEqual(['2', '3', '1'])
    expect(bySeed.s1.status).toBe('所持中') // 持っているのは、名前ではなく同じ枠（s1）のまま
    expect(bySeed.s2.status).toBe('未所持')
    expect((await byVersion('2'))!.seedId).toBe('s1')
  })

  it('コレクション名が直されても、カードはついていく', async () => {
    await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'MD', '1', 's1']]))
    const col = (await db.collections.toArray())[0]
    const card = (await db.cards.toArray())[0]
    const r = await importCsv('name,type,releaseDate,id\nアルバム A（改）,アルバム（韓国盤）,2026-01-01,colA\n', cardsCsv([['アルバム A（改）', 'ユジン', 'MD', '1', 's1']]))
    expect(r.renamedCollections).toBe(1)
    expect(r.addedCollections).toBe(0)
    expect(await db.collections.count()).toBe(1)
    expect((await db.collections.get(col.id))!.name).toBe('アルバム A（改）')
    expect((await db.cards.get(card.id))!.collectionId).toBe(col.id)
    expect(await db.cards.count()).toBe(1)
  })

  it('変わらない取り込みは何も増やさない', async () => {
    const csv = cardsCsv([['アルバム A', 'ユジン', 'MD', '1', 's1'], ['アルバム A', 'ガウル', 'MD', '1', 's2']])
    await importCsv(COLS, csv)
    const r = await importCsv(COLS, csv)
    expect([r.addedCards, r.renamedCards, r.adoptedCards, r.skippedCards]).toEqual([0, 0, 0, 2])
  })

  it('id 列のない古い形の CSV は、これまでどおり名前で探す', async () => {
    const old = 'collection,member,source,version\nアルバム A,ユジン,MD,1\n'
    const oldCols = 'name,type,releaseDate\nアルバム A,アルバム（韓国盤）,2026-01-01\n'
    await importCsv(oldCols, old)
    const r = await importCsv(oldCols, old)
    expect([r.addedCards, r.skippedCards]).toEqual([0, 1])
  })

  it('id が重なっている初期データは断る（壊れている）', async () => {
    await expect(importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'MD', '1', 'dup'], ['アルバム A', 'ガウル', 'MD', '1', 'dup']]))).rejects.toThrow('id が重なっています')
  })

  it('初期データから外れた昔の枠は、消さずに残す（整理のページで見る）', async () => {
    await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'MD', '1', 's1'], ['アルバム A', 'ガウル', 'MD', '1', 's2']]))
    await importCsv(COLS, cardsCsv([['アルバム A', 'ユジン', 'MD', '1', 's1']])) // s2 が初期データから消えた
    expect(await db.cards.count()).toBe(2)
  })

  it('消す一覧（removed.csv）に名前があっても、いまの初期データに ID がある枠は消さない', async () => {
    const csv = cardsCsv([['アルバム A', 'ユジン', 'MD', '1', 's1']])
    await importCsv(COLS, csv)
    const removed = 'collection,member,source,version\nアルバム A,ユジン,MD,1\n'
    expect(await removeObsolete(removed, csv)).toBe(0)
    expect(await db.cards.count()).toBe(1)
  })
})
