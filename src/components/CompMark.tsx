import { MEMBERS } from '../lib/members'

/**
 * コンプの印（2026-11-26、pocamaster のために描いた）。
 * 6 つの山の王冠。山の先に 6 人のメンバーカラーの粒を、メンバーの順に置く（6 人そろった＝コンプ）。
 * 線は細い金色 1 本だけで、塗りはしない
 */
const GOLD = '#C9A23A'
const PEAKS = [6, 15.6, 25.2, 34.8, 44.4, 54]

export function CompMark({ size = 56, label }: { size?: number; label?: string }) {
  return (
    <svg
      width={size}
      height={(size * 46) / 60}
      viewBox="0 0 60 46"
      role={label ? 'img' : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
    >
      <path
        d="M6 36 L6 12 L10.8 27 L15.6 12 L20.4 27 L25.2 12 L30 27 L34.8 12 L39.6 27 L44.4 12 L49.2 27 L54 12 L54 36 Z"
        fill="none"
        stroke={GOLD}
        strokeWidth={1.4}
        strokeLinejoin="round"
      />
      <line x1={6} y1={40.5} x2={54} y2={40.5} stroke={GOLD} strokeWidth={1.4} strokeLinecap="round" />
      {PEAKS.map((x, i) => (
        <circle key={x} cx={x} cy={7.5} r={2.6} fill={MEMBERS[i].color} />
      ))}
    </svg>
  )
}
