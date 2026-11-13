import { describe, expect, it } from 'vitest'
import { missedText, updateMissed } from './imageMissed'
import type { ImageZipInfo } from './imageImport'

const diff = (seq: number): ImageZipInfo => ({ kind: 'diff', seq, base: seq - 1, date: '2026-11-13', count: 1 })
const full = (seq: number): ImageZipInfo => ({ kind: 'full', seq, date: '2026-11-13', count: 1 })

describe('入らなかった画像の枚数の記録', () => {
  it('差分で入らなかった画像があれば、その番号で残す', () => {
    expect(updateMissed(undefined, diff(56), 3)).toEqual({ '56': 3 })
  })

  it('同じ差分を入れ直して全部入ったら、その番号だけ消す', () => {
    expect(updateMissed({ '55': 2, '56': 3 }, diff(56), 0)).toEqual({ '55': 2 })
  })

  it('別の差分が全部入っても、前の差分の記録は消さない', () => {
    expect(updateMissed({ '55': 2 }, diff(56), 0)).toEqual({ '55': 2 })
  })

  it('全部入りを取り込んだら、前の記録は置き換える', () => {
    expect(updateMissed({ '55': 2, '56': 3 }, full(56), 0)).toEqual({})
    expect(updateMissed({ '55': 2 }, full(56), 4)).toEqual({ full: 4 })
  })

  it('番号のない ZIP（表紙など）では変えない', () => {
    expect(updateMissed({ '55': 2 }, undefined, 1)).toEqual({ '55': 2 })
    expect(updateMissed(undefined, undefined, 0)).toEqual({})
  })

  it('設定に出す文：なければ空、あれば合計と番号', () => {
    expect(missedText(undefined)).toBe('')
    expect(missedText({})).toBe('')
    expect(missedText({ '56': 3, '55': 2 })).toContain('5 枚あります（差分 No.55・差分 No.56）')
    expect(missedText({ full: 4 })).toContain('4 枚あります（全部入り）')
  })
})
