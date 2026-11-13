import type { ImageZipInfo } from './imageImport'

/**
 * 画像の ZIP を取り込んだとき、対応するカードがなくて入らなかった画像の枚数（settings の 'imageZipMissed'）。
 * 取り込みの直後の文は画面を閉じると消えるので、設定に出し続けるために残す（2026-11-13）。
 * キーは差分の番号（'56' など）か、全部入りの 'full'
 */
export type ImageMissed = Record<string, number>

/**
 * 取り込みの結果で、入らなかった枚数の記録を書き換える。
 * - 差分：その番号の枚数を入れる。0 枚なら、その番号の記録を消す（入れ直して全部入った）
 * - 全部入り：全部の画像が入っているので、前の記録は全部これに置き換える
 * - 番号のない ZIP（表紙の ZIP など）：カードの画像の版とは関係がないので、変えない
 */
export function updateMissed(prev: ImageMissed | undefined, info: ImageZipInfo | undefined, miss: number): ImageMissed {
  if (!info) return prev ?? {}
  if (info.kind !== 'diff') return miss > 0 ? { full: miss } : {}
  const next = { ...prev }
  if (miss > 0) next[String(info.seq)] = miss
  else delete next[String(info.seq)]
  return next
}

/** 設定に出す文。入らなかった画像がなければ空 */
export function missedText(missed: ImageMissed | undefined): string {
  const keys = Object.keys(missed ?? {}).filter((k) => missed![k] > 0)
  if (keys.length === 0) return ''
  const total = keys.reduce((n, k) => n + missed![k], 0)
  const names = keys
    .sort((a, b) => (a === 'full' ? -1 : b === 'full' ? 1 : Number(a) - Number(b)))
    .map((k) => (k === 'full' ? '全部入り' : `差分 No.${k}`))
    .join('・')
  return `入らなかった画像が ${total} 枚あります（${names}）。「初期データを取り込む」をしてから、同じ ZIP をもう一度取り込んでください`
}
