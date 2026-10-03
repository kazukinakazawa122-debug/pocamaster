import { db, deleteImages, type Card, type MyAlbum } from './db'

/**
 * 初期データにない枠の整理（2026-10-03）。固定の ID（seedId）がない枠は、
 * 昔の名前のまま取り残された枠（名前・番号を付け替えられて、初期データとつながらなくなった枠）か、自分で作ったカード。
 * 「自分の枠として残す」にしたものは除く
 */
export async function listOrphans(): Promise<Card[]> {
  return (await db.cards.toArray()).filter((c) => !c.seedId && !c.keepAsOwn)
}

/** 付け替え先の候補：同じコレクションの、同じメンバーの初期データの枠。持っていない枠・同じ入手元の枠を先に */
export function candidatesFor(orphan: Card, all: Card[]): Card[] {
  const members = [...orphan.memberIds].sort().join('+')
  return all
    .filter((c) => c.seedId && c.collectionId === orphan.collectionId && c.id !== orphan.id && [...c.memberIds].sort().join('+') === members)
    .sort(
      (a, b) =>
        Number(a.status === '所持中') - Number(b.status === '所持中') ||
        Number(b.source === orphan.source) - Number(a.source === orphan.source) ||
        a.order - b.order,
    )
}

/**
 * 取り残された枠の記録（持っている・お気に入り・譲・画像・状態の履歴・マイアルバムのポケット）を、初期データの枠へ移して、取り残された枠を消す。
 * 移し先がすでに持っている・画像があるときは、その状態を優先する（画像は移し先になければ移す）
 */
export async function mergeCardInto(orphan: Card, target: Card): Promise<void> {
  const moveImage = !target.imageId && !!orphan.imageId
  const owned = orphan.status === '所持中' || target.status === '所持中'
  const changes: Partial<Card> = {
    status: owned ? '所持中' : target.status,
    statusChangedAt: orphan.status === '所持中' && target.status !== '所持中' ? orphan.statusChangedAt : target.statusChangedAt,
    ...(orphan.favorite || target.favorite ? { favorite: true } : {}),
    ...(orphan.trade || target.trade ? { trade: true } : {}),
    ...(moveImage ? { imageId: orphan.imageId, imageCredit: orphan.imageCredit, imageHash: orphan.imageHash } : {}),
  }
  await db.transaction('rw', [db.cards, db.statusHistory, db.myAlbums, db.images, db.thumbs], async () => {
    await db.cards.update(target.id, changes)
    await db.statusHistory.where('cardId').equals(orphan.id).modify({ cardId: target.id })
    await db.myAlbums
      .filter((a) => a.slots.includes(orphan.id))
      .modify((a: MyAlbum) => {
        a.slots = a.slots.map((s) => (s === orphan.id ? target.id : s))
      })
    await db.cards.delete(orphan.id)
    if (orphan.imageId && !moveImage) await deleteImages([orphan.imageId])
  })
}

/** 初期データにない枠だが、自分の枠として残す */
export async function keepAsOwn(card: Card): Promise<void> {
  await db.cards.update(card.id, { keepAsOwn: true })
}
