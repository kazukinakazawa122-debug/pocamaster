import { useEffect, useRef, useState } from 'react'
import { CompMark } from './CompMark'

/**
 * コンプしたときの表示（2026-11-26）。
 * トレカの形の札に、pocamaster の王冠（CompMark）とコレクション名。札の縁はトレカの縁のような細い二重の線で、
 * ホロのような光が一度だけ斜めに通る。紙吹雪などの決まった飾りは使わない（本人の要望）。
 * 見ている間に「まだそろっていない」から「全部そろった」に変わったときだけ出す（開いたときにもうコンプしていたら出さない）。
 * 下の画面はそのまま押せる（「元に戻す」も）。2.4 秒で消える。iPhone の「視差効果を減らす」がオンなら光は通さない
 */
export function Celebrate({ complete, name }: { complete: boolean; name: string }) {
  const prev = useRef(complete)
  const [show, setShow] = useState(false)

  useEffect(() => {
    if (complete && !prev.current) setShow(true)
    if (!complete) setShow(false)
    prev.current = complete
  }, [complete])

  useEffect(() => {
    if (!show) return
    const t = window.setTimeout(() => setShow(false), 2400)
    return () => window.clearTimeout(t)
  }, [show])

  if (!show) return null
  return (
    <div className="celebrate" role="status">
      <div className="comp-card">
        <CompMark size={64} />
        <div className="comp-title">COMPLETE</div>
        <div className="comp-name">{name}</div>
      </div>
    </div>
  )
}
