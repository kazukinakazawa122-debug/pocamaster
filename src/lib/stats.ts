import type { Card, CardStatus, StatusHistory } from './db'
import type { MemberId } from './members'

export interface Progress {
  owned: number
  total: number
  /** 0〜100 の整数。カードがなければ null（「—」表示） */
  pct: number | null
}

export function progress(cards: Card[]): Progress {
  const owned = cards.filter((c) => c.status === '所持中').length
  const total = cards.length
  return { owned, total, pct: total === 0 ? null : Math.floor((owned / total) * 100) }
}

/** そのメンバーが写っているカード（ソロ・ユニット両方）で計算する */
export function memberProgress(cards: Card[], id: MemberId): Progress {
  return progress(cards.filter((c) => c.memberIds.includes(id)))
}

export function isComplete(p: Progress): boolean {
  return p.total > 0 && p.owned === p.total
}

export function pctText(p: Progress): string {
  return p.pct === null ? '—' : `${p.pct}%`
}

/**
 * 状態を切り替えた記録（古い順）から、本当に状態が変わった分だけを取り出す。d は「所持中」になったら +1、「所持中」でなくなったら -1。
 * 同じカードで、前の記録と同じ状態への記録は数えない（素早く 2 回押したときにできた二重の記録。2026-10-14 に直す前のもの）
 */
export function effectiveChanges(history: StatusHistory[]): { h: StatusHistory; d: 1 | -1 }[] {
  const state = new Map<string, CardStatus>()
  const out: { h: StatusHistory; d: 1 | -1 }[] = []
  for (const h of history) {
    const before = state.get(h.cardId) ?? h.from
    state.set(h.cardId, h.to)
    if (before === h.to) continue
    out.push({ h, d: h.to === '所持中' ? 1 : -1 })
  }
  return out
}
