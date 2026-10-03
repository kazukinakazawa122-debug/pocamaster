import { beforeEach, describe, expect, it } from 'vitest'
import { addImages, db, getFull, setCardStatus } from './db'
import { candidatesFor, keepAsOwn, listOrphans, mergeCardInto } from './orphans'
import { card, collection, jpeg, resetDb } from '../test/helpers'

describe('初期データにない枠の整理', () => {
  beforeEach(async () => {
    await resetDb()
    await db.collections.add(collection())
  })

  it('固定の ID のない枠だけが一覧に出る。「自分の枠として残す」にしたものは出ない', async () => {
    await db.cards.bulkAdd([card({ id: 'seed', seedId: 's1' }), card({ id: 'old', version: '旧' }), card({ id: 'mine', version: '自作' })])
    expect((await listOrphans()).map((c) => c.id).sort()).toEqual(['mine', 'old'])
    await keepAsOwn((await db.cards.get('mine'))!)
    expect((await listOrphans()).map((c) => c.id)).toEqual(['old'])
  })

  it('付け替え先の候補は、同じコレクションの同じメンバーの初期データの枠（持っていない枠・同じ入手元が先）', async () => {
    await db.collections.add(collection({ id: 'col2', name: '別の盤' }))
    await db.cards.bulkAdd([
      card({ id: 'orphan', source: 'QQ', version: '旧' }),
      card({ id: 'c1', seedId: 'a', source: 'MD', order: 1 }),
      card({ id: 'c2', seedId: 'b', source: 'QQ', order: 2 }),
      card({ id: 'c3', seedId: 'c', source: 'QQ', order: 3, status: '所持中' }),
      card({ id: 'other-member', seedId: 'd', memberIds: ['gaeul'] }),
      card({ id: 'other-col', seedId: 'e', collectionId: 'col2' }),
      card({ id: 'no-seed', source: 'QQ' }),
    ])
    const all = await db.cards.toArray()
    expect(candidatesFor((await db.cards.get('orphan'))!, all).map((c) => c.id)).toEqual(['c2', 'c1', 'c3'])
  })

  it('記録（持っている・お気に入り・譲・履歴・マイアルバム・画像）を移して、取り残された枠を消す', async () => {
    await addImages([{ id: 'img', full: jpeg('f'), thumb: jpeg('t') }])
    await db.cards.bulkAdd([card({ id: 'orphan', version: '旧', favorite: true, trade: true, imageId: 'img' }), card({ id: 'target', seedId: 's', version: '新' })])
    await setCardStatus((await db.cards.get('orphan'))!, '所持中')
    await db.myAlbums.add({ id: 'al', name: 'マイ', slots: ['orphan', null, null, null, null, null, null, null, null], createdAt: 1 })
    await mergeCardInto((await db.cards.get('orphan'))!, (await db.cards.get('target'))!)

    expect(await db.cards.get('orphan')).toBeUndefined()
    const t = (await db.cards.get('target'))!
    expect([t.status, t.favorite, t.trade, t.imageId]).toEqual(['所持中', true, true, 'img'])
    expect(await getFull('img')).toBeTruthy() // 画像は移し先に移った（消えない）
    expect((await db.statusHistory.toArray()).every((h) => h.cardId === 'target')).toBe(true)
    expect((await db.myAlbums.get('al'))!.slots[0]).toBe('target')
  })

  it('移し先にすでに画像があるときは移し先の画像を使い、取り残された枠の画像は消す', async () => {
    await addImages([
      { id: 'own', full: jpeg('own'), thumb: jpeg('own-t') },
      { id: 'zip', full: jpeg('zip'), thumb: jpeg('zip-t') },
    ])
    await db.cards.bulkAdd([card({ id: 'orphan', version: '旧', imageId: 'own' }), card({ id: 'target', seedId: 's', version: '新', imageId: 'zip', imageCredit: '@作者' })])
    await mergeCardInto((await db.cards.get('orphan'))!, (await db.cards.get('target'))!)
    expect((await db.cards.get('target'))!.imageId).toBe('zip')
    expect(await getFull('own')).toBeUndefined()
    expect(await getFull('zip')).toBeTruthy()
  })

  it('移し先がすでに持っているなら、持っている状態のまま（持っていない枠の記録で上書きしない）', async () => {
    await db.cards.bulkAdd([card({ id: 'orphan', version: '旧' }), card({ id: 'target', seedId: 's', version: '新', status: '所持中', statusChangedAt: 50 })])
    await mergeCardInto((await db.cards.get('orphan'))!, (await db.cards.get('target'))!)
    const t = (await db.cards.get('target'))!
    expect([t.status, t.statusChangedAt]).toEqual(['所持中', 50])
  })
})
