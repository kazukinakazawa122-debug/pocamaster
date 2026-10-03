import { beforeEach, describe, expect, it } from 'vitest'
import { db, getFull, getThumb } from './db'
import { importImages } from './imageImport'
import { card, collection, imageZip, resetDb } from '../test/helpers'

describe('画像の取り込み', () => {
  beforeEach(async () => {
    await resetDb()
    await db.collections.add(collection())
    await db.cards.bulkAdd([card({ id: 'a' }), card({ id: 'b', memberIds: ['gaeul'] }), card({ id: 'ab', memberIds: ['yujin', 'gaeul'], version: 'U' })])
  })

  it('コレクション・メンバー・入手元・バージョンが合うカードに画像を付け、出典も記録する', async () => {
    const zip = await imageZip([
      { collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A', credit: '@作者' },
      { collection: 'テスト盤', members: ['ユジン', 'ガウル'], source: '本体封入', version: 'U' }, // ユニット
    ])
    const r = await importImages(zip)
    expect(r.matched).toBe(2)
    expect(r.unmatched).toEqual([])
    const a = (await db.cards.get('a'))!
    expect(a.imageCredit).toBe('@作者')
    expect(await (await getFull(a.imageId!))!.text()).toBe('full-0')
    expect(await (await getThumb(a.imageId!))!.text()).toBe('thumb-0')
    expect((await db.cards.get('ab'))!.imageId).toBeTruthy()
    expect((await db.cards.get('b'))!.imageId).toBeUndefined()
  })

  it('枠のない画像は取り込まず、一覧に出す', async () => {
    const zip = await imageZip([
      { collection: 'テスト盤', members: ['リズ'], source: '本体封入', version: 'A' }, // 枠がない
      { collection: 'ないコレクション', members: ['ユジン'], source: 'x', version: '' },
    ])
    const r = await importImages(zip)
    expect(r.matched).toBe(0)
    expect(r.unmatched).toHaveLength(2)
  })

  it('同じカードに取り込み直すと画像を置き換え、前の画像は消す', async () => {
    const e = { collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A' }
    await importImages(await imageZip([e]))
    const first = (await db.cards.get('a'))!.imageId!
    await importImages(await imageZip([e]))
    const second = (await db.cards.get('a'))!.imageId!
    expect(second).not.toBe(first)
    expect(await getFull(first)).toBeUndefined()
    expect(await db.thumbs.get(first)).toBeUndefined()
    expect(await db.images.count()).toBe(1)
  })

  it('表紙（cover）はコレクションの表紙になる', async () => {
    const zip = await imageZip([{ collection: 'テスト盤', members: [], source: '', version: '', cover: true }])
    const r = await importImages(zip)
    expect(r.matched).toBe(1)
    expect((await db.collections.get('col1'))!.coverImageId).toBeTruthy()
  })

  it('画像の ZIP ではないファイルは断る', async () => {
    await expect(importImages(new Blob(['x']))).rejects.toThrow()
  })

  it('版（info.json）を読み、check が false なら取り込まない（差分 ZIP の取り込み忘れの確認用）', async () => {
    const zip = await imageZip([{ collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A' }], { kind: 'diff', seq: 5, base: 4, date: '2026-10-03', count: 1 })
    const r = await importImages(zip, undefined, (info) => info?.seq === 6)
    expect(r.canceled).toBe(true)
    expect(r.info?.seq).toBe(5)
    expect((await db.cards.get('a'))!.imageId).toBeUndefined()
  })

  it('進み具合を知らせる', async () => {
    const calls: [number, number][] = []
    await importImages(await imageZip([{ collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A' }]), (d, t) => calls.push([d, t]))
    expect(calls.at(-1)).toEqual([1, 1])
  })
})
