import { beforeEach, describe, expect, it } from 'vitest'
import { db, getFull, getThumb } from './db'
import { importImages } from './imageImport'
import { card, collection, imageZip, resetDb } from '../test/helpers'

const E_A = { collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A' }
const E_B = { collection: 'テスト盤', members: ['ガウル'], source: '本体封入', version: 'A' }

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
    await importImages(await imageZip([e], undefined, '-v2')) // 中身が変わった画像
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

  it('同じ画像の取り込み直しは書き込まず、とばす（全部入りを取り込み直しても速い）', async () => {
    const zip = await imageZip([E_A, E_B])
    const r1 = await importImages(zip)
    expect([r1.matched, r1.skipped]).toEqual([2, 0])
    const idA = (await db.cards.get('a'))!.imageId
    const r2 = await importImages(zip)
    expect([r2.matched, r2.skipped]).toEqual([0, 2])
    expect((await db.cards.get('a'))!.imageId).toBe(idA) // 画像の id も変わらない
    expect(await db.images.count()).toBe(2)
  })

  it('途中で止まった取り込みは、続きから入る（入った分はとばす）', async () => {
    await importImages(await imageZip([E_A])) // 1 枚だけ入ったところで止まったつもり
    const r = await importImages(await imageZip([E_A, E_B]))
    expect([r.matched, r.skipped]).toEqual([1, 1])
    expect((await db.cards.get('b'))!.imageId).toBeTruthy()
  })

  it('中身が変わった画像、出典が変わった画像は書き換える', async () => {
    await importImages(await imageZip([E_A]))
    const r1 = await importImages(await imageZip([E_A], undefined, 'x'))
    expect([r1.matched, r1.skipped]).toEqual([1, 0])
    const r2 = await importImages(await imageZip([{ ...E_A, credit: '@新しい出典' }], undefined, 'x'))
    expect([r2.matched, r2.skipped]).toEqual([1, 0])
    expect((await db.cards.get('a'))!.imageCredit).toBe('@新しい出典')
  })

  it('画像が実際には残っていないカードは、指紋が残っていてもとばさず入れ直す', async () => {
    const zip = await imageZip([E_A])
    await importImages(zip)
    const id = (await db.cards.get('a'))!.imageId!
    await db.images.delete(id) // 画像だけ失われた（保存の失敗など）
    const r = await importImages(zip)
    expect([r.matched, r.skipped]).toEqual([1, 0])
    expect(await getFull((await db.cards.get('a'))!.imageId!)).toBeTruthy()
  })

  it('読み込めない画像が 1 枚あっても、残りは取り込む（失敗の一覧に出す）', async () => {
    // 一覧用の画像のない entry は、縮める処理（このテスト環境にはない）が要るので失敗する → 1 枚の失敗のまねになる
    const bad = await imageZip([E_A], undefined, '', true)
    const good = await imageZip([E_B])
    const JSZip = (await import('jszip')).default
    const merged = new JSZip()
    const m1 = JSON.parse(await (await JSZip.loadAsync(bad)).file('manifest.json')!.async('string'))
    const m2 = JSON.parse(await (await JSZip.loadAsync(good)).file('manifest.json')!.async('string')).map((e: { file: string; thumb: string }) => ({ ...e, file: 'g/' + e.file, thumb: 'g/' + e.thumb }))
    const zb = await JSZip.loadAsync(bad)
    const zg = await JSZip.loadAsync(good)
    for (const n of Object.keys(zb.files)) if (n !== 'manifest.json' && !zb.files[n].dir) merged.file(n, await zb.file(n)!.async('arraybuffer'))
    for (const n of Object.keys(zg.files)) if (n !== 'manifest.json' && !zg.files[n].dir) merged.file('g/' + n, await zg.file(n)!.async('arraybuffer'))
    merged.file('manifest.json', JSON.stringify([...m1, ...m2]))
    const r = await importImages(await merged.generateAsync({ type: 'blob' }))
    expect(r.failed).toHaveLength(1)
    expect(r.matched).toBe(1)
    expect((await db.cards.get('b'))!.imageId).toBeTruthy()
    expect((await db.cards.get('a'))!.imageId).toBeUndefined()
  })
})
