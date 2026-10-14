import { beforeEach, describe, expect, it } from 'vitest'
import { db, deleteCards, setCardStatus, setCardsStatus } from './db'
import { changeCardStatus, loadCards, peekCards, toggleCardStatus } from './cardStore'
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

/** タップで切り替える（2026-10-14：素早く 2 回押すと、2 回目が古い状態のまま処理され、元に戻らず記録も二重になっていた） */
describe('タップで切り替える', () => {
  beforeEach(async () => {
    await resetDb()
    await db.collections.add(collection())
    await db.cards.bulkAdd([card({ id: 'a' }), card({ id: 'b', memberIds: ['gaeul'] })])
    await loadCards()
    await settle()
  })
  const history = async () => (await db.statusHistory.orderBy('id').toArray()).map((h) => `${h.cardId}:${h.from}→${h.to}`)

  it('手元の記録は保存を待たずにすぐ変わる（画面にすぐ出る）', async () => {
    const { from, to, done } = toggleCardStatus((await db.cards.get('a'))!)
    expect([from, to]).toEqual(['未所持', '所持中'])
    expect(status('a')).toBe('所持中') // 保存が終わる前に、もう変わっている
    await done
    expect((await db.cards.get('a'))!.status).toBe('所持中')
    expect(await history()).toEqual(['a:未所持→所持中'])
  })

  it('画面が古いまま続けて 2 回押しても、押した回数だけ切り替わり（元に戻る）、記録は「行って戻る」の 2 件', async () => {
    const stale = (await db.cards.get('a'))! // 画面に出ているカード（描き直しが追いつかず、未所持のまま）
    const first = toggleCardStatus(stale)
    const second = toggleCardStatus(stale)
    expect(second.to).toBe('未所持')
    expect(status('a')).toBe('未所持')
    await Promise.all([first.done, second.done])
    await settle()
    expect((await db.cards.get('a'))!.status).toBe('未所持')
    expect(status('a')).toBe('未所持') // 1 回目の保存の結果で、手元の記録が「所持中」に戻ったままにならない
    expect(await history()).toEqual(['a:未所持→所持中', 'a:所持中→未所持'])
  })

  it('「元に戻す」（変える前の状態にする）も、すぐ手元の記録に出て、保存される', async () => {
    const c = (await db.cards.get('a'))!
    const { from, done } = toggleCardStatus(c)
    await done
    await changeCardStatus(c, from)
    expect(status('a')).toBe('未所持')
    expect((await db.cards.get('a'))!.status).toBe('未所持')
    expect(await history()).toEqual(['a:未所持→所持中', 'a:所持中→未所持'])
  })

  it('保存に失敗したら、先に変えた手元の記録を元に戻す', async () => {
    // 保存の途中でわざと失敗させる（iPhone の空き容量がいっぱいのときなどのまね）
    const fail = () => {
      throw new Error('保存に失敗')
    }
    db.cards.hook('updating', fail)
    try {
      const p = changeCardStatus((await db.cards.get('b'))!, '所持中')
      expect(status('b')).toBe('所持中') // 保存の前に、先に変わる
      await expect(p).rejects.toThrow()
    } finally {
      db.cards.hook('updating').unsubscribe(fail)
    }
    await settle()
    expect((await db.cards.get('b'))!.status).toBe('未所持')
    expect(status('b')).toBe('未所持') // 読み直して、データベースと同じに戻った
  })
})
