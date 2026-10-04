/**
 * スクロール位置を覚える（「戻る」で元の位置に戻すため）。
 * スクロールのたびに window.scrollY を読むと、そのとき増えた画像の分の「まだ計算していない配置」を、その場で計算させてしまい、
 * スクロールがひっかかる（2026-10-04 の調査で、速いスクロール中の処理時間の約 15%）。
 * スクロール中は読まず、止まって少したってから読む。ページを移る前の「押した」ときにも読む（止まる前に移っても位置が合うように）
 */
export function watchScroll(save: (y: number) => void): () => void {
  let timer: number | undefined
  const onScroll = () => {
    window.clearTimeout(timer)
    timer = window.setTimeout(() => save(window.scrollY), 150)
  }
  const onClick = () => save(window.scrollY)
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onClick, true)
  // 下のタブは指を離したときに画面を移る（click ではない）ので、押し始めにも読む
  document.addEventListener('pointerdown', onClick, true)
  return () => {
    window.clearTimeout(timer)
    window.removeEventListener('scroll', onScroll)
    document.removeEventListener('click', onClick, true)
    document.removeEventListener('pointerdown', onClick, true)
  }
}
