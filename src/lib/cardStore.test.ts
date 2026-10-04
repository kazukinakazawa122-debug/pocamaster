import { beforeEach, describe, expect, it } from 'vitest'
import { db, deleteCards, setCardStatus, setCardsStatus } from './db'
import { loadCards, peekCards } from './cardStore'
import { card, collection, resetDb } from '../test/helpers'

const settle = () => new Promise((r) => setTimeout(r, 30))
const status = (id: string) => peekCards()?.find((c) => c.id === id)?.status

/** 手元の記録（全カードの写し）が、データベースと食い違わないこと。食い違うと、画面と本当のデータがずれる */
describe('手元のカードの記録', () => {
  beforeEach(async () => {
    await resetDb()
    await db.collections.add(collection())
    await db.cards.bulkAdd([card({ id: 'a' }), card({ id: 'b', memberIds: ['gaeul'] })])
    await loadCards()
    await settle()
  })

  it('足す・変える・消す が手元の記録にも反映される', async () => {
    expect(peekCards()?.length).toBe(2)
    await setCardStatus((await db.cards.get('a'))!, '所持中')
    expect(status('a')).toBe('所持中')
    await setCardsStatus([(await db.cards.get('b'))!], '所持中')
    expect(status('b')).toBe('所持中')
    await deleteCards([(await db.cards.get('a'))!])
    expect(peekCards()?.map((c) => c.id)).toEqual(['b'])
  })

  it('保存のまとまりが途中で取り消されたら、手元の記録も元に戻す（データベースと食い違わせない）', async () => {
    await expect(
      db.transaction('rw', db.cards, async () => {
        await db.cards.update('a', { status: '所持中' })
        expect(status('a')).toBe('所持中') // 書けた時点では手元も変わる
        throw new Error('途中で失敗')
      }),
    ).rejects.toThrow('途中で失敗')
    await settle()
    expect((await db.cards.get('a'))!.status).toBe('未所持') // データベースは元に戻った
    expect(status('a')).toBe('未所持') // 手元の記録も元に戻った
  })
})
