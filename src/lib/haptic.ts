/**
 * 押したときに iPhone を軽く震わせる（2026-11-26）。
 * iPhone の Safari には震わせる命令（navigator.vibrate）がないため、iOS 18 から使える「スイッチ」の部品を
 * 見えない所に置いて押す（スイッチを押すと iPhone が軽く震える）。
 * 使えない端末（Android は vibrate を使う・古い iPhone・パソコン）では何も起きないだけ
 */
let label: HTMLLabelElement | null = null

export function tapHaptic() {
  if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
    navigator.vibrate(8)
    return
  }
  if (typeof document === 'undefined') return
  if (!label) {
    label = document.createElement('label')
    label.setAttribute('aria-hidden', 'true')
    label.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none'
    const input = document.createElement('input')
    input.type = 'checkbox'
    input.setAttribute('switch', '')
    input.tabIndex = -1
    label.appendChild(input)
    document.body.appendChild(label)
  }
  label.click()
}
