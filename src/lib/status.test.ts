import { beforeEach, describe, expect, it } from 'vitest'
import { db, restoreCardsStatus, setCardStatus, setCardsStatus, type Card, type StatusHistory } from './db'
import { effectiveChanges } from './stats'
import { card, collection, resetDb } from '../test/helpers'

const history = async () => (await db.statusHistory.orderBy('id').toArray()).map((h) => `${h.cardId}:${h.from}→${h.to}`)

/** 状態の保存は、渡されたカード（画面の古い状態のことがある）ではなく、保存してある最新の状態から決める（2026-10-14） */
describe('状態の保存', () => {
  beforeEach(async () => {
    await resetDb()
    await db.collections.add(collection())
    await db.cards.bulkAdd([card({ id: 'a' }), card({ id: 'b', memberIds: ['gaeul'] }), card({ id: 'c', memberIds: ['rei'] })])
  })

  it('古いカードで同じ状態に 2 回しても、記録は 1 件だけ', async () => {
    const stale = (await db.cards.get('a'))!
    await setCardStatus(stale, '所持中')
    await setCardStatus(stale, '所持中') // stale は「未所持」のままだが、保存してあるのはもう「所持中」
    expect((await db.cards.get('a'))!.status).toBe('所持中')
    expect(await history()).toEqual(['a:未所持→所持中'])
  })

  it('まとめて切り替えも、もうその状態のカードは変えず、実際に変えたカードの前の姿を返す。元に戻すと、その分だけ戻る', async () => {
    const [a, b, c] = (await db.cards.bulkGet(['a', 'b', 'c'])) as Card[]
    await setCardStatus(a, '所持中') // a は先に持っている（選んだ画面の状態は古いまま）
    const before = await setCardsStatus([a, b, c], '所持中')
    expect(before.map((x) => `${x.id}:${x.status}`)).toEqual(['b:未所持', 'c:未所持'])
    expect(await history()).toEqual(['a:未所持→所持中', 'b:未所持→所持中', 'c:未所持→所持中'])

    await restoreCardsStatus(before)
    const after = await db.cards.bulkGet(['a', 'b', 'c'])
    expect(after.map((x) => x!.status)).toEqual(['所持中', '未所持', '未所持']) // a は前から持っていたので、そのまま
    expect(await history()).toEqual(['a:未所持→所持中', 'b:未所持→所持中', 'c:未所持→所持中', 'b:所持中→未所持', 'c:所持中→未所持'])
  })

  it('元に戻す前に、ほかで同じ状態に戻していたら、記録を足さない', async () => {
    const b = (await db.cards.get('b'))!
    const before = await setCardsStatus([b], '所持中')
    await setCardStatus(b, '未所持') // 先に 1 枚だけ戻した
    await restoreCardsStatus(before)
    expect(await history()).toEqual(['b:未所持→所持中', 'b:所持中→未所持'])
  })
})

/** 集めた記録の数え方：同じ状態への記録が続いたもの（二重の記録）は 1 回と数える */
describe('本当に状態が変わった記録だけを数える', () => {
  const h = (cardId: string, from: '未所持' | '所持中', to: '未所持' | '所持中', changedAt: number): StatusHistory => ({ cardId, from, to, changedAt })
  const sum = (list: StatusHistory[]) => effectiveChanges(list).reduce((n, x) => n + x.d, 0)

  it('ふつうの記録は、そのまま +1・-1', () => {
    expect(sum([h('a', '未所持', '所持中', 1), h('b', '未所持', '所持中', 2), h('a', '所持中', '未所持', 3)])).toBe(1)
  })

  it('素早く 2 回押してできた二重の記録（同じ向きが続く）は 1 回と数える', () => {
    const list = [h('a', '未所持', '所持中', 1), h('a', '未所持', '所持中', 2)]
    expect(sum(list)).toBe(1)
    expect(effectiveChanges(list).map((x) => x.h.changedAt)).toEqual([1]) // 数えるのは最初の 1 件（その月に数える）
    expect(sum([h('a', '所持中', '未所持', 1), h('a', '所持中', '未所持', 2)])).toBe(-1)
  })

  it('ほかのカードの記録をはさんでも、カードごとに見分ける', () => {
    expect(sum([h('a', '未所持', '所持中', 1), h('b', '未所持', '所持中', 2), h('a', '未所持', '所持中', 3), h('b', '所持中', '未所持', 4)])).toBe(1)
  })
})
