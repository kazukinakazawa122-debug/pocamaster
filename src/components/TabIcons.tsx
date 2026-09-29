/**
 * 下のタブのアイコンのうち、Tabler Icons にない形のもの（本人の要望、2026-09-29）
 * Tabler と同じく 24×24・線の太さを揃えて描く
 */
interface Props {
  size?: number
  stroke?: number
  'aria-hidden'?: boolean
}

/** 実績：取っ手・台座・星のついたトロフィー */
export function TrophyIcon({ size = 24, stroke = 1.6, ...rest }: Props) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...rest}>
      {/* カップ */}
      <path d="M7 3.5h10v4.5a5 5 0 0 1 -10 0z" />
      {/* 取っ手 */}
      <path d="M7 5h-2.2a.8.8 0 0 0 -.8.8v.7a3.5 3.5 0 0 0 3.4 3.5" />
      <path d="M17 5h2.2a.8.8 0 0 1 .8.8v.7a3.5 3.5 0 0 1 -3.4 3.5" />
      {/* 首と台座 */}
      <path d="M12 13v2.5" />
      <path d="M9.5 15.5h5l.6 2.3h-6.2z" />
      <path d="M6.5 17.8h11v3h-11z" />
      {/* 星 */}
      <path d="M12 5.4l.7 1.4 1.5 .2 -1.1 1 .3 1.5 -1.4 -.7 -1.4 .7 .3 -1.5 -1.1 -1 1.5 -.2z" strokeWidth={stroke * 0.7} />
    </svg>
  )
}
