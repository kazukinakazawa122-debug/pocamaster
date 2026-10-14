import { useEffect, useSyncExternalStore } from 'react'
import Dexie from 'dexie'
import { db, setCardStatus, type Card, type CardStatus } from './db'

/**
 * カードの記録をアプリの中に 1 回だけ読んでおく（本人の報告、2026-10-02「まだ読み込みが長い」）。
 * ホーム・コレクション一覧・検索・求／譲・集めた記録は、ここから数える（開くたびに 6,000 枚を読み直さない）。
 * 書き換えはこのファイルの最後のフック（cards の creating / updating / deleting）で、変わったカードだけを直す
 */
let byId: Map<string, Card> | null = null
let list: Card[] | null = null
let loading: Promise<void> | null = null
const listeners = new Set<() => void>()
let notifyScheduled = false
/** 読み込みの途中に書き換えがあった（読み終わったあとに読み直す） */
let dirtyDuringLoad = false
/**
 * 保存が終わる前に、手元の記録だけ先に変えた値（カードの id → 変えた項目と、何回目の変更か。2026-10-14）。
 * 前のタップの保存が終わって届いた値で、あとから押した値を上書きしない（画面が一瞬もどらないように）
 */
const pending = new Map<string, { changes: Partial<Card>; seq: number }>()
let pendingSeq = 0

function notify() {
  list = null
  // まとめて書き換えたとき（数千枚）に、1 枚ごとに画面を描き直さないよう、まとめて知らせる。
  // setTimeout だと、画面が隠れているときや重いときに待ちが大きく延びるので、すぐあと（microtask）にする
  if (notifyScheduled) return
  notifyScheduled = true
  queueMicrotask(() => {
    notifyScheduled = false
    listeners.forEach((l) => l())
  })
}

/** アプリを開いたらすぐ読み始める。2 回目からは何もしない */
export function loadCards(): Promise<void> {
  loading ??= db.cards.toArray().then((all) => {
    if (dirtyDuringLoad) {
      dirtyDuringLoad = false
      loading = null
      return loadCards()
    }
    byId = new Map(all.map((c) => [c.id, c]))
    notify()
  })
  return loading
}

/** 読み直す（バックアップから戻したときなど、全部が入れ替わったとき） */
export function reloadCards(): Promise<void> {
  loading = null
  byId = null
  pending.clear()
  return loadCards()
}

function cardPut(card: Card) {
  if (!byId) {
    if (loading) dirtyDuringLoad = true
    return
  }
  const p = pending.get(card.id)
  byId.set(card.id, p ? { ...card, ...p.changes } : card)
  notify()
}

function cardRemoved(id: string) {
  if (!byId) {
    if (loading) dirtyDuringLoad = true
    return
  }
  if (!byId.delete(id)) return
  notify()
}

/**
 * カードの状態を変える。手元の記録を保存の前に先に変えるので、画面にすぐ出る（保存を待たない。2026-10-14）。
 * 保存に失敗したら読み直して元に戻す（失敗はそのまま投げるので、main.tsx の「保存できませんでした」も出る）
 */
export function changeCardStatus(card: Card, to: CardStatus): Promise<void> {
  const now = Date.now()
  const seq = ++pendingSeq
  const latest = byId?.get(card.id)
  if (byId && latest) {
    const changes = { status: to, statusChangedAt: now }
    pending.set(card.id, { changes, seq })
    byId.set(card.id, { ...latest, ...changes })
    notify()
  }
  const done = () => {
    if (pending.get(card.id)?.seq === seq) pending.delete(card.id)
  }
  return setCardStatus(card, to, now).then(done, (e) => {
    done()
    void reloadCards()
    throw e
  })
}

/**
 * タップで「持っている」⇄「持っていない」を切り替える。向きは、渡された card（画面の古い状態のことがある）ではなく、
 * 手元の記録のいちばん新しい状態から決める（描き直しが追いつく前に続けて押しても、押した回数だけ切り替わる。2026-10-14）
 */
export function toggleCardStatus(card: Card): { from: CardStatus; to: CardStatus; done: Promise<void> } {
  const from = (byId?.get(card.id) ?? card).status
  const to: CardStatus = from === '所持中' ? '未所持' : '所持中'
  return { from, to, done: changeCardStatus(card, to) }
}

/** いま手元にある全カード（画面を使わずに確かめる用。読み終わるまでは undefined） */
export function peekCards(): Card[] | undefined {
  return snapshot()
}

function snapshot(): Card[] | undefined {
  if (!byId) return undefined
  list ??= [...byId.values()]
  return list
}

function subscribe(l: () => void) {
  listeners.add(l)
  return () => listeners.delete(l)
}

/** 全部のカード（読み終わるまでは undefined）。カードが変わると新しい配列になる */
export function useAllCards(): Card[] | undefined {
  useEffect(() => {
    loadCards()
  }, [])
  return useSyncExternalStore(subscribe, snapshot)
}

/**
 * 手元の記録は、1 件の書き込みが成功した時点で直す。そのあと同じ保存のまとまり（トランザクション）が取り消されると
 * （途中の別の書き込みの失敗など）、データベースは元に戻るのに、手元の記録だけ変わったままになる。取り消されたら読み直す
 */
const watched = new WeakSet<object>()
function watchAbort() {
  const tx = Dexie.currentTransaction
  if (!tx || watched.has(tx)) return
  watched.add(tx)
  tx.on('abort', () => {
    void reloadCards()
  })
}

// カードを足す・変える・消すたびに、手元の記録も同じように直す（画像の取り込み・まとめて切り替える・削除なども、すべてここを通る）
db.cards.hook('creating', function (_key, obj) {
  watchAbort()
  this.onsuccess = () => cardPut({ ...obj })
})
db.cards.hook('updating', function () {
  watchAbort()
  this.onsuccess = (updated) => cardPut(updated as Card)
})
db.cards.hook('deleting', function (key) {
  watchAbort()
  this.onsuccess = () => cardRemoved(key as string)
})
