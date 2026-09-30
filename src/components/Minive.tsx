/**
 * MINIVE（IVE の公式キャラクター）の飾り（本人の要望、2026-09-30）。線画のシリーズだけを使う（3D は使わない）
 * 画像は public/minive/：
 * - park/row.png … IVE Wiki の「MINIVE PARK」ポスターの、手をつないで走る 6 人（コレクション）。left・right はその左右半分（ホーム）
 * - flat/ … IVE Wiki の立ち姿のイラスト（マイアルバム）
 * - face/ … IVE Wiki の MINIVE ポスターの、ピンクの枠の顔の絵（設定）
 */
const BASE = `${import.meta.env.BASE_URL}minive/`
// ユジン・ガウル・レイ・ウォニョン・リズ・イソ の順
const ORDER = ['puppy', 'squirrel', 'chick', 'rabbit', 'cat', 'bear']

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

/**
 * ホームのロゴの左右に 3 人ずつ。コレクションと同じ PARK の 6 人の帯を、ネコとリスの間のすき間で 2 つに分けたもの
 * （本人の要望、2026-09-30：送ってもらった画像の切り抜きより、こちらの方がきれい）
 */
export function MiniveTrio({ side }: { side: 'left' | 'right' }) {
  return (
    <span className="minive-trio" aria-hidden>
      <img src={`${BASE}park/${side}.png`} alt="" />
    </span>
  )
}
