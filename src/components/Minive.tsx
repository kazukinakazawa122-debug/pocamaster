/**
 * MINIVE（IVE の公式キャラクター）の飾り（本人の要望、2026-09-30）
 * 画像は public/minive/：
 * - *.png … 本人が送った公式画像（走っているポーズ）から 1 人ずつ切り抜いたもの
 * - 3d/ … IVE Wiki（Fandom）の「キャラクター紹介」の 3D の絵から切り抜いたもの
 * - flat/ … IVE Wiki の立ち姿のイラスト（背景が透明の画像）
 */
const BASE = `${import.meta.env.BASE_URL}minive/`
// ユジン・ガウル・レイ・ウォニョン・リズ・イソ の順
const ORDER = ['puppy', 'squirrel', 'chick', 'rabbit', 'cat', 'bear']
const TOP = ['squirrel', 'bear', 'chick']
const BOTTOM = ['rabbit', 'puppy', 'cat']

export type MiniveStyle = 'run' | '3d' | 'flat' | 'mix'

function src(style: Exclude<MiniveStyle, 'mix'>, name: string): string {
  return style === 'run' ? `${BASE}${name}.png` : `${BASE}${style}/${name}.png`
}

/** 画面のタイトルの横に 6 人を並べる（動かさない）。画面ごとに違う絵にする */
export function MiniveRun({ style = 'run' }: { style?: MiniveStyle }) {
  return (
    <div className={`minive-run minive-${style}`} aria-hidden>
      {ORDER.map((n, i) => (
        <img key={n} src={src(style === 'mix' ? (i % 2 ? 'flat' : '3d') : style, n)} alt="" />
      ))}
    </div>
  )
}

/** ホームのロゴの左右に 3 人ずつ（左は上の段の 3 人、右は下の段の 3 人）。動かさない */
export function MiniveTrio({ side }: { side: 'left' | 'right' }) {
  const names = side === 'left' ? TOP : BOTTOM
  return (
    <span className="minive-trio" aria-hidden>
      {names.map((n) => (
        <img key={n} src={src('run', n)} alt="" />
      ))}
    </span>
  )
}
