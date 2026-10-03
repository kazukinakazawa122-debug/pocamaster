import { beforeEach, describe, expect, it } from 'vitest'
import JSZip from 'jszip'
import { addImages, db, getFull } from './db'
import { exportOwnImages, listOwnImageCards, OWN_IMAGE_CREDIT } from './ownImages'
import { importImages } from './imageImport'
import { card, collection, imageZip, jpeg, resetDb } from '../test/helpers'

/** アプリで切り取った画像を ZIP にしてパソコンに残す。ZIP から取り込んだ画像は含めず、画像の ZIP で上書きもしない */
describe('自分で登録した画像', () => {
  beforeEach(async () => {
    await resetDb()
    await db.collections.add(collection())
    await db.cards.bulkAdd([
      card({ id: 'own', seedId: 's-own', imageId: 'own-img' }), // 自分で切り取った（出典なし）
      card({ id: 'zip', memberIds: ['gaeul'], imageId: 'zip-img', imageCredit: '@作者', imageHash: 'abc' }), // 画像の ZIP から
      card({ id: 'none', memberIds: ['rei'] }),
    ])
    await addImages([
      { id: 'own-img', full: jpeg('own-full'), thumb: jpeg('own-thumb') },
      { id: 'zip-img', full: jpeg('zip-full'), thumb: jpeg('zip-thumb') },
    ])
  })

  it('出典のない画像があるカードだけを数える', async () => {
    expect((await listOwnImageCards()).map((c) => c.id)).toEqual(['own'])
  })

  it('画像の ZIP と同じ形（manifest.json ＋ 画像）に書き出す', async () => {
    const r = (await exportOwnImages())!
    expect([r.count, r.skipped]).toEqual([1, 0])
    expect(r.file.name).toMatch(/^pocamaster-own-images-\d{8}\.zip$/)
    const zip = await JSZip.loadAsync(r.file)
    const manifest = JSON.parse(await zip.file('manifest.json')!.async('string'))
    expect(manifest).toHaveLength(1)
    expect(manifest[0]).toMatchObject({ collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A', credit: OWN_IMAGE_CREDIT, seedId: 's-own' })
    expect(await zip.file(manifest[0].file)!.async('string')).toBe('own-full')
    expect(await zip.file(manifest[0].thumb)!.async('string')).toBe('own-thumb')
  })

  it('書き出した ZIP は、そのまま「画像をまとめて取り込む」で読める（別の端末・入れ直したあとでも戻る）', async () => {
    const r = (await exportOwnImages())!
    await db.cards.update('own', { imageId: undefined })
    await db.images.clear()
    await db.thumbs.clear()
    const res = await importImages(r.file)
    expect([res.matched, res.unmatched.length]).toEqual([1, 0])
    const c = (await db.cards.get('own'))!
    expect(await (await getFull(c.imageId!))!.text()).toBe('own-full')
  })

  it('書き出せる画像がなければ、何も作らない', async () => {
    await db.cards.update('own', { imageId: undefined })
    expect(await exportOwnImages()).toBeNull()
  })

  it('画像の ZIP で、自分で切り取った画像を置き換えない。ZIP から取り込んだ画像は置き換える', async () => {
    const zip = await imageZip([
      { collection: 'テスト盤', members: ['ユジン'], source: '本体封入', version: 'A', credit: '@作者' }, // own の枠
      { collection: 'テスト盤', members: ['ガウル'], source: '本体封入', version: 'A', credit: '@作者' }, // zip の枠
    ], undefined, '-new')
    const r = await importImages(zip)
    expect([r.matched, r.keptOwn]).toEqual([1, 1])
    expect((await db.cards.get('own'))!.imageId).toBe('own-img') // 変わらない
    expect((await db.cards.get('zip'))!.imageId).not.toBe('zip-img') // 置き換わった
  })

  it('出典の空の画像を ZIP から取り込んでも、「自分の画像」にならない', async () => {
    const zip = await imageZip([{ collection: 'テスト盤', members: ['レイ'], source: '本体封入', version: 'A' }])
    await importImages(zip)
    expect((await db.cards.get('none'))!.imageCredit).toBeTruthy()
    expect((await listOwnImageCards()).map((c) => c.id)).toEqual(['own'])
  })
})
