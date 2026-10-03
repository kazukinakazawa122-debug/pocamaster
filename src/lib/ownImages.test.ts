import { beforeEach, describe, expect, it } from 'vitest'
import JSZip from 'jszip'
import { addImages, db, getFull } from './db'
import { exportOwnImages, listOwnImageCards, listUnexportedOwnImageCards, markExported, OWN_IMAGE_CREDIT } from './ownImages'
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

  it('書き出した画像が ZIP に入って取り込まれたら（中身が同じ）、「自分の画像」の枚数から外れる。画像そのものは書き換えない', async () => {
    const r = (await exportOwnImages())!
    expect((await listOwnImageCards()).length).toBe(1)
    const before = (await db.cards.get('own'))!.imageId
    const res = await importImages(r.file) // パソコンの全部入りの ZIP に入った、と同じ中身
    expect([res.adoptedOwn, res.keptOwn, res.matched]).toEqual([1, 0, 0])
    const c = (await db.cards.get('own'))!
    expect(c.imageId).toBe(before) // 画像は書き換えない
    expect([c.imageCredit, !!c.imageHash]).toEqual([OWN_IMAGE_CREDIT, true])
    expect(await listOwnImageCards()).toEqual([]) // 書き出しの枚数は 0 になる
    expect(await exportOwnImages()).toBeNull()
    // もう一度取り込んでも、とばす
    const again = await importImages(r.file)
    expect([again.skipped, again.adoptedOwn]).toEqual([1, 0])
  })

  it('書き出したあとに切り直した画像は、ZIP の画像と中身がちがうので、「自分の画像」のまま残る', async () => {
    const r = (await exportOwnImages())!
    // 書き出したあとで、同じカードの画像を切り直した
    await addImages([{ id: 'own-img2', full: jpeg('own-full-recropped'), thumb: jpeg('own-thumb2') }])
    await db.cards.update('own', { imageId: 'own-img2' })
    const res = await importImages(r.file)
    expect([res.adoptedOwn, res.keptOwn]).toEqual([0, 1])
    expect((await listOwnImageCards()).map((c) => c.id)).toEqual(['own'])
  })

  it('書き出して保存した画像は「書き出し済み」になり、次からは新しい画像だけを書き出す（同じものを何度も書き出さない）', async () => {
    const r1 = (await exportOwnImages())!
    expect(r1.imageIds).toEqual(['own-img'])
    // 保存をやめたとき（markExported を呼ばない）は、まだ書き出していない扱い
    expect((await listUnexportedOwnImageCards()).length).toBe(1)
    await markExported(r1.imageIds) // 「ファイルに保存する」まで終えた
    expect(await listUnexportedOwnImageCards()).toEqual([])
    expect(await exportOwnImages()).toBeNull()
    // 新しく切り取った画像だけが、次の ZIP に入る
    await addImages([{ id: 'new-img', full: jpeg('new-full'), thumb: jpeg('new-thumb') }])
    await db.cards.update('none', { imageId: 'new-img' })
    const r2 = (await exportOwnImages())!
    expect([r2.count, r2.imageIds]).toEqual([1, ['new-img']])
    const manifest = JSON.parse(await (await JSZip.loadAsync(r2.file)).file('manifest.json')!.async('string'))
    expect(manifest.map((e: { members: string[] }) => e.members[0])).toEqual(['レイ'])
  })

  it('全部を書き出し直す（all）と、書き出し済みの画像も入る', async () => {
    await markExported(['own-img'])
    expect(await exportOwnImages()).toBeNull()
    const r = (await exportOwnImages({ all: true }))!
    expect(r.count).toBe(1)
  })

  it('書き出したあとに切り直した画像（新しい id）は、また書き出し対象になる', async () => {
    await markExported(['own-img'])
    await addImages([{ id: 'own-img-v2', full: jpeg('v2'), thumb: jpeg('v2t') }])
    await db.cards.update('own', { imageId: 'own-img-v2' })
    expect((await listUnexportedOwnImageCards()).map((c) => c.id)).toEqual(['own'])
  })

  it('書き出し済みの記録は、バックアップに入って戻る', async () => {
    await markExported(['own-img'])
    const { exportBackup, restoreBackup } = await import('./backup')
    const { file } = await exportBackup()
    await resetDb()
    await restoreBackup(file)
    expect((await db.settings.get('ownExportedImageIds'))!.value).toEqual(['own-img'])
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
