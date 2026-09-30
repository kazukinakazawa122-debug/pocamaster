/**
 * MINIVE（IVE の公式キャラクター）の飾り（本人の要望、2026-09-30）。線画のシリーズだけを使う（3D は使わない）
 * 画像は public/minive/：
 * - *.png … 本人が送った公式画像（走っているポーズ）から 1 人ずつ切り抜いたもの（ホーム）
 * - park/row.png … IVE Wiki の「MINIVE PARK」ポスターの、手をつないで走る 6 人（コレクション）
 * - flat/ … IVE Wiki の立ち姿のイラスト（マイアルバム）
 * - face/ … IVE Wiki の MINIVE ポスターの、ピンクの枠の顔の絵（設定）
 */
const BASE = `${import.meta.env.BASE_URL}minive/`
// ユジン・ガウル・レイ・ウォニョン・リズ・イソ の順
const ORDER = ['puppy', 'squirrel', 'chick', 'rabbit', 'cat', 'bear']
const TOP = ['squirrel', 'bear', 'chick']
const BOTTOM = ['rabbit', 'puppy', 'cat']

export type MiniveStyle = 'park' | 'flat' | 'face'

/** 画面のタイトルの横に並べる（動かさない）。画面ごとに違う絵にする */
export function MiniveRun({ style }: { style: MiniveStyle }) {
  if (style === 'park') {
    return (
      <div className="minive-run minive-park" aria-hidden>
        <img src={`${BASE}park/row.png`} alt="" />
      </div>
    )
  }
  return (
    <div className={`minive-run minive-${style}`} aria-hidden>
      {ORDER.map((n) => (
        <img key={n} src={`${BASE}${style}/${n}.png`} alt="" />
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
        <img key={n} src={`${BASE}${n}.png`} alt="" />
      ))}
    </span>
  )
}
