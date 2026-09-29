/**
 * 下のタブのアイコンのうち、Tabler Icons にない形のもの（本人の要望、2026-09-29）
 * Tabler と同じく 24×24・線の太さを揃えて描く
 */
interface Props {
  size?: number
  stroke?: number
  'aria-hidden'?: boolean
}

/** ホーム：IVE のロゴ（public/ive-logo.png の形を、いまの文字色で塗る） */
export function IveLogoIcon({ size = 24 }: Props) {
  return <span className="tab-logo" style={{ width: size, height: size }} aria-hidden />
}

/** マイアルバム：3×3 のポケットのあるバインダー */
export function AlbumIcon({ size = 24, stroke = 1.6, ...rest }: Props) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" {...rest}>
      {/* 表紙 */}
      <rect x="4" y="3" width="16" height="18" rx="2" />
      {/* とじ具 */}
      <path d="M4 7h-1.2M4 12h-1.2M4 17h-1.2" />
      {/* ポケット 3×3 */}
      {[6.5, 10.9, 15.3].flatMap((y) =>
        [7, 10.8, 14.6].map((x) => <rect key={`${x}-${y}`} x={x} y={y} width="2.6" height="3.2" rx=".5" strokeWidth={stroke * 0.7} />),
      )}
    </svg>
  )
}
