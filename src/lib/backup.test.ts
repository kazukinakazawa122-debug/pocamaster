import { beforeEach, describe, expect, it } from 'vitest'
import JSZip from 'jszip'
import { addImages, db, getFull, getThumb, setCardStatus } from './db'
import { changesSinceBackup, exportBackup, markBackedUp, restoreBackup, verifyBackup } from './backup'
import { card, collection, jpeg, resetDb } from '../test/helpers'

/** バックアップは「データを失わない」ための最後の砦。書き出し → 全部消す → 戻す で同じになることを確かめる */
describe('バックアップ', () => {
  beforeEach(resetDb)

  async function seed() {
    await db.collections.add(collection())
    await db.cards.bulkAdd([
      card({ id: 'owned', status: '所持中', favorite: true, imageId: 'own-img' }), // 自分で登録した画像
      card({ id: 'zipimg', memberIds: ['gaeul'], imageId: 'zip-img', imageCredit: '@作者' }), // 画像 ZIP から取り込んだ画像
      card({ id: 'plain', memberIds: ['rei'] }),
    ])
    await addImages([
      { id: 'own-img', full: jpeg('own-full'), thumb: jpeg('own-thumb') },
      { id: 'zip-img', full: jpeg('zip-full'), thumb: jpeg('zip-thumb') },
    ])
    await db.statusHistory.add({ cardId: 'owned', from: '未所持', to: '所持中', changedAt: 5 })
    await db.myAlbums.add({ id: 'a1', name: 'マイ', slots: ['owned', null, null, null, null, null, null, null, null], createdAt: 1 })
    await db.settings.put({ key: 'profile', value: { name: 'テスト' } })
  }

  it('書き出して全部消し、戻すと同じになる（ZIP から取り込んだ画像は戻らない）', async () => {
    await seed()
    const { file, skipped } = await exportBackup()
    expect(skipped).toBe(0)

    await resetDb()
    expect(await db.cards.count()).toBe(0)
    await restoreBackup(file)

    expect(await db.collections.count()).toBe(1)
    const cards = await db.cards.toArray()
    expect(cards.map((c) => c.id).sort()).toEqual(['owned', 'plain', 'zipimg'])
    const owned = cards.find((c) => c.id === 'owned')!
    expect(owned.status).toBe('所持中')
    expect(owned.favorite).toBe(true)
    // 自分の画像は戻る
    expect(await (await getFull('own-img'))!.text()).toBe('own-full')
    expect(await (await getThumb('own-img'))!.text()).toBe('own-thumb')
    // ZIP から取り込んだ画像は戻らない（imageId も外れる。ZIP を取り込み直す）
    expect(cards.find((c) => c.id === 'zipimg')!.imageId).toBeUndefined()
    expect(await getFull('zip-img')).toBeUndefined()
    // 記録・マイアルバム・設定
    expect(await db.statusHistory.count()).toBe(1)
    expect((await db.myAlbums.get('a1'))!.slots[0]).toBe('owned')
    expect((await db.settings.get('profile'))!.value).toEqual({ name: 'テスト' })
  })

  it('戻したバックアップの日が「最後のバックアップ」になる', async () => {
    await seed()
    const { file } = await exportBackup()
    await resetDb()
    await restoreBackup(file)
    expect((await db.settings.get('lastBackupAt'))!.value).toBeGreaterThan(0)
  })

  it('バックアップではないファイルは断る（今のデータは消さない）', async () => {
    await seed()
    await expect(restoreBackup(jpeg('not a zip'))).rejects.toThrow()
    const z = new JSZip()
    z.file('hello.txt', 'x')
    await expect(restoreBackup(await z.generateAsync({ type: 'blob' }))).rejects.toThrow('バックアップファイルではありません')
    expect(await db.cards.count()).toBe(3)
  })

  it('確認：枚数が合わないバックアップは失敗にする', async () => {
    await seed()
    const { file } = await exportBackup()
    await expect(verifyBackup(file, { cards: 3, collections: 1, images: 1 })).resolves.toBeUndefined()
    await expect(verifyBackup(file, { cards: 4, collections: 1, images: 1 })).rejects.toThrow('カードの数')
    await expect(verifyBackup(file, { cards: 3, collections: 1, images: 2 })).rejects.toThrow('画像の数')
  })

  it('最後のバックアップのあとの変更を数える', async () => {
    await seed()
    expect(await changesSinceBackup()).toBe(1) // 記録 1 件（バックアップしたことがない）
    await markBackedUp()
    expect(await changesSinceBackup()).toBe(0)
    await new Promise((r) => setTimeout(r, 5))
    await setCardStatus((await db.cards.get('plain'))!, '所持中')
    expect(await changesSinceBackup()).toBe(1)
  })
})
