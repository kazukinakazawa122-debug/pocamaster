import { useEffect } from 'react'
import { db, restoreCardsStatus, setCardsStatus, type Card, type CardStatus } from '../lib/db'
import { useUndo } from './Undo'

interface Props {
  /** 選んでいるカード */
  selected: Card[]
  /** いま見えているカード（「すべて選ぶ」の対象） */
  visible: Card[]
  onSelectAll: (cards: Card[]) => void
  onClear: () => void
  /** 選ぶのをやめる */
  onDone: () => void
}

/**
 * まとめて切り替える（本人の要望、2026-10-01：アルバムを開けたときに 1 枚ずつ押すのは大変）。
 * 選んでいる間は下のタブの代わりに出す。操作したら選ぶのを終える（「元に戻す」付き）
 */
export default function SelectBar({ selected, visible, onSelectAll, onClear, onDone }: Props) {
  const showUndo = useUndo()
  // 選んでいる間は下のタブを隠す（このバーと重ならないように）
  useEffect(() => {
    document.documentElement.classList.add('selecting')
    return () => document.documentElement.classList.remove('selecting')
  }, [])

  const n = selected.length
  const allSelected = visible.length > 0 && visible.every((c) => selected.some((s) => s.id === c.id))
  const allTrade = n > 0 && selected.every((c) => c.trade)

  const setStatus = async (to: CardStatus) => {
    // 元に戻すのは、実際に変えたカードだけ（変える前の状態は、保存してある最新のものから）
    const before = await setCardsStatus(selected, to)
    showUndo(`${n} 枚を${to}にしました`, () => restoreCardsStatus(before))
    onDone()
  }
  const setTrade = async () => {
    const snapshot = selected.map((c) => ({ id: c.id, trade: c.trade }))
    const to = !allTrade
    await db.cards.bulkUpdate(snapshot.map((c) => ({ key: c.id, changes: { trade: to } })))
    // 譲れるのは持っているカードなので、印を付けるときは「所持中」にもする
    const owned = to ? await setCardsStatus(selected, '所持中') : []
    showUndo(to ? `${n} 枚に「譲」の印を付けました` : `${n} 枚の「譲」の印を外しました`, async () => {
      await db.cards.bulkUpdate(snapshot.map((c) => ({ key: c.id, changes: { trade: c.trade } })))
      await restoreCardsStatus(owned)
    })
    onDone()
  }

  return (
    <div className="select-bar" role="toolbar" aria-label="選んだカードをまとめて切り替える">
      <div className="select-bar-row">
        <span className="small" style={{ flex: 1 }}>
          <span className="num">{n}</span> 枚を選んでいます
        </span>
        <button className="chip" onClick={() => (allSelected ? onClear() : onSelectAll(visible))}>
          {allSelected ? '選ぶのを外す' : '見えているのを全部'}
        </button>
        <button className="chip" onClick={onDone}>
          やめる
        </button>
      </div>
      <div className="select-bar-row">
        <button className="btn primary" style={{ flex: 1 }} disabled={n === 0} onClick={() => setStatus('所持中')}>
          所持中にする
        </button>
        <button className="btn" style={{ flex: 1 }} disabled={n === 0} onClick={() => setStatus('未所持')}>
          未所持にする
        </button>
        <button className="btn" disabled={n === 0} onClick={setTrade} aria-label={allTrade ? '「譲」の印を外す' : '「譲」の印を付ける'}>
          {allTrade ? '譲を外す' : '譲'}
        </button>
      </div>
    </div>
  )
}
