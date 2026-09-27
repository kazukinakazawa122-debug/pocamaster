import type { Card } from './db'
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
