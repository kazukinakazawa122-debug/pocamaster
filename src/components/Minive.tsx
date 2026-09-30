/**
 * MINIVE（IVE の公式キャラクター）の飾り（本人の要望、2026-09-30）
 * 画像は public/minive/（本人が送った公式画像から 1 人ずつ切り抜いたもの）
 */
const BASE = `${import.meta.env.BASE_URL}minive/`
const TOP = ['squirrel', 'bear', 'chick']
const BOTTOM = ['rabbit', 'puppy', 'cat']

/** 画面のタイトルの横に 6 人を並べる（走っているポーズのイラスト。動かさない） */
export function MiniveRun() {
  return (
    <div className="minive-run" aria-hidden>
      {[...TOP, ...BOTTOM].map((n) => (
        <img key={n} src={`${BASE}${n}.png`} alt="" />
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
