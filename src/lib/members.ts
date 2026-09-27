export type MemberId = 'yujin' | 'gaeul' | 'rei' | 'wonyoung' | 'liz' | 'leeseo'

export interface Member {
  id: MemberId
  name: string
  /** 塗りの色 */
  color: string
  /** 白い背景の上で文字に使う色 */
  text: string
  /** 塗りの上に置く文字の色 */
  on: string
}

// 06_デザインシステム 2.1 のメンバーカラー
export const MEMBERS: Member[] = [
  { id: 'yujin', name: 'ユジン', color: '#378ADD', text: '#185FA5', on: '#ffffff' },
  { id: 'gaeul', name: 'ガウル', color: '#F08A3C', text: '#A8561A', on: '#ffffff' },
  { id: 'rei', name: 'レイ', color: '#F2C230', text: '#9A7400', on: '#27272a' },
  { id: 'wonyoung', name: 'ウォニョン', color: '#E85A9C', text: '#A8336A', on: '#ffffff' },
  { id: 'liz', name: 'リズ', color: '#3FB56B', text: '#237A44', on: '#ffffff' },
  { id: 'leeseo', name: 'イソ', color: '#E24B4A', text: '#A32D2D', on: '#ffffff' },
]

export const MEMBER_BY_ID = Object.fromEntries(MEMBERS.map((m) => [m.id, m])) as Record<MemberId, Member>
export const MEMBER_BY_NAME = Object.fromEntries(MEMBERS.map((m) => [m.name, m])) as Record<string, Member>

export function memberOrder(id: MemberId): number {
  return MEMBERS.findIndex((m) => m.id === id)
}

/** メンバー名をメンバー順に並べる。6 人全員なら ['全員'] */
export function memberNames(ids: MemberId[]): string[] {
  if (ids.length === MEMBERS.length) return ['全員']
  return [...ids].sort((a, b) => memberOrder(a) - memberOrder(b)).map((id) => MEMBER_BY_ID[id].name)
}

/** 仮カードや一覧に出すメンバー名 */
export function memberLabel(ids: MemberId[]): string {
  return memberNames(ids).join('・')
}
