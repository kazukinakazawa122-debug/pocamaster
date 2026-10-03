import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { IconArrowDown, IconArrowLeft, IconArrowRight, IconArrowUp } from '@tabler/icons-react'
import { makeImage } from '../lib/image'
import { defaultQuad, nearestCorner, nudge, outputSize, warp, type Point, type Quad } from '../lib/warp'

interface Props {
  file: File
  /** 切り取ったカードの画像（大きい画像と一覧用）を渡す。保存は呼んだ側で行う */
  onDone: (img: { full: Blob; thumb: Blob }) => Promise<void>
  onClose: () => void
}

const LOUPE = 112
const ZOOM = 3
const HANDLE = 20 // 画面上の点の大きさ（px）
const GRAB = 72 // 押した位置から、この距離（px）までの角を動かす（点そのものでなく、まわりを押しても動く）
const NAMES = ['左上', '右上', '右下', '左下']

/**
 * 実物のカードの写真から、カードの四隅を合わせて、まっすぐな 1 枚の画像を切り取る（2026-10-03、アプリの改善 44.【2】）。
 * フリマの出品写真・自分で撮った写真・6 枚並びの写真のどれでも使える。
 * 押しやすさ（本人の要望）：①点のまわりのどこを押しても、いちばん近い角が動く ②押した位置のまま動く（点が指の位置へ飛ばない）
 * ③写真は画面におさまる大きさ（縦長の写真でも、ページを動かせる） ④選んだ角を 1 ピクセルずつ動かすボタン（長押しで連続）
 * ⑤ドラッグ中は、点のまわりを拡大して見せる（指で隠れないように）
 */
export default function PhotoCropper({ file, onDone, onClose }: Props) {
  // 写真の仮の URL。useMemo で作ると、開発モードの二重実行で先に片付けられて写真が出なくなるので、effect の中で作って持つ
  const [url, setUrl] = useState('')
  useEffect(() => {
    const u = URL.createObjectURL(file)
    setUrl(u)
    return () => URL.revokeObjectURL(u)
  }, [file])
  const boxRef = useRef<HTMLDivElement>(null)
  const [size, setSize] = useState<{ w: number; h: number } | null>(null) // 写真の大きさ（向きを直したあと）
  const [quad, setQuad] = useState<Quad | null>(null)
  const [shown, setShown] = useState(0) // 画面に出している写真の幅（px）
  const [drag, setDrag] = useState<number | null>(null)
  const [sel, setSel] = useState(0) // 微調整の対象の角
  const grab = useRef<Point>({ x: 0, y: 0 }) // 押した位置と角のずれ（画面の px）
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState<{ full: Blob; thumb: Blob; url: string } | null>(null)
  useEffect(() => {
    if (!preview) return
    return () => URL.revokeObjectURL(preview.url)
  }, [preview])

  useEffect(() => {
    const el = boxRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setShown(el.clientWidth))
    ro.observe(el)
    setShown(el.clientWidth)
    return () => ro.disconnect()
  }, [size, preview])

  const scale = size && shown ? shown / size.w : 1 // 画面の px ÷ 写真の px
  const pts: Point[] | undefined = quad?.map((p) => ({ x: p.x * scale, y: p.y * scale }))
  const shownH = size ? shown * (size.h / size.w) : 0

  const local = (e: React.PointerEvent): Point => {
    const r = boxRef.current!.getBoundingClientRect()
    return { x: e.clientX - r.left, y: e.clientY - r.top }
  }

  const onDown = (e: React.PointerEvent) => {
    if (!pts) return
    const p = local(e)
    const i = nearestCorner(pts, p, GRAB)
    if (i === null) return
    e.currentTarget.setPointerCapture(e.pointerId)
    grab.current = { x: pts[i].x - p.x, y: pts[i].y - p.y } // 押した位置のまま動かす
    setDrag(i)
    setSel(i)
  }
  const onMove = (e: React.PointerEvent) => {
    if (drag === null || !size || !quad) return
    const p = local(e)
    const x = Math.min(size.w, Math.max(0, (p.x + grab.current.x) / scale))
    const y = Math.min(size.h, Math.max(0, (p.y + grab.current.y) / scale))
    setQuad(quad.map((q, k) => (k === drag ? { x, y } : q)) as Quad)
  }

  // 微調整：画面の 1px ぶんずつ（写真が大きいほど、写真の 1px は画面で小さいので、画面の px で動かす）
  const step = (dx: number, dy: number) => {
    if (!size) return
    setQuad((q) => (q ? nudge(q, sel, dx / scale, dy / scale, size.w, size.h) : q))
  }
  const hold = useRef<number | undefined>(undefined)
  const stopHold = () => {
    window.clearTimeout(hold.current)
    window.clearInterval(hold.current)
  }
  const startHold = (dx: number, dy: number) => {
    step(dx, dy)
    stopHold()
    hold.current = window.setTimeout(() => {
      hold.current = window.setInterval(() => step(dx, dy), 60)
    }, 350)
  }
  useEffect(() => stopHold, [])

  const crop = async () => {
    if (!quad || !size) return
    setBusy(true)
    setError('')
    try {
      // 四隅を含む範囲だけを取り出す（12MP の写真全体を展開しない）
      const xs = quad.map((p) => p.x)
      const ys = quad.map((p) => p.y)
      const x0 = Math.max(0, Math.floor(Math.min(...xs)) - 2)
      const y0 = Math.max(0, Math.floor(Math.min(...ys)) - 2)
      const x1 = Math.min(size.w, Math.ceil(Math.max(...xs)) + 2)
      const y1 = Math.min(size.h, Math.ceil(Math.max(...ys)) + 2)
      const bmp = await createImageBitmap(file, { imageOrientation: 'from-image' })
      const cv = document.createElement('canvas')
      cv.width = x1 - x0
      cv.height = y1 - y0
      const ctx = cv.getContext('2d')!
      ctx.drawImage(bmp, x0, y0, cv.width, cv.height, 0, 0, cv.width, cv.height)
      bmp.close()
      const src = ctx.getImageData(0, 0, cv.width, cv.height)
      const q = quad.map((p) => ({ x: p.x - x0, y: p.y - y0 })) as Quad
      const { width, height } = outputSize(q)
      const out = warp({ width: src.width, height: src.height, data: src.data }, q, width, height)
      const oc = document.createElement('canvas')
      oc.width = width
      oc.height = height
      oc.getContext('2d')!.putImageData(new ImageData(out.data as Uint8ClampedArray<ArrayBuffer>, width, height), 0, 0)
      // このあと makeImage でもう一度縮めて保存するので、ここでは画質を高めに
      const blob = await new Promise<Blob>((res, rej) => oc.toBlob((b) => (b ? res(b) : rej(new Error('画像を作れませんでした'))), 'image/jpeg', 0.95))
      const img = await makeImage(blob)
      setPreview({ ...img, url: URL.createObjectURL(img.full) })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusy(false)
    }
  }

  const save = async () => {
    if (!preview) return
    setBusy(true)
    try {
      await onDone({ full: preview.full, thumb: preview.thumb })
      onClose()
    } catch (e) {
      setError((e as Error).message)
      setBusy(false)
    }
  }

  const arrow = (label: string, dx: number, dy: number, Icon: typeof IconArrowUp) => (
    <button
      className="btn"
      aria-label={`${NAMES[sel]}の点を${label}へ動かす`}
      style={{ width: 56, height: 48, padding: 0, touchAction: 'manipulation' }}
      onPointerDown={(e) => {
        e.preventDefault()
        startHold(dx, dy)
      }}
      onPointerUp={stopHold}
      onPointerLeave={stopHold}
      onPointerCancel={stopHold}
      onContextMenu={(e) => e.preventDefault()}
    >
      <Icon size={22} aria-hidden />
    </button>
  )

  return createPortal(
    <div
      style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'var(--bg)', overflowY: 'auto', padding: 'calc(var(--safe-top) + 12px) 16px calc(var(--safe-bottom) + 16px)' }}
      role="dialog"
      aria-modal="true"
    >
      <div style={{ maxWidth: 560, margin: '0 auto' }}>
        <div style={{ fontWeight: 700, marginBottom: 6 }}>{preview ? 'この画像で登録しますか？' : '写真から切り取る'}</div>
        {!preview && (
          <div className="small muted" style={{ marginBottom: 10 }}>
            カードの四隅に、赤い点を合わせてください。点の近くを押して動かすと、いちばん近い点が動きます。ななめに撮った写真でも、まっすぐに直します。
          </div>
        )}

        {preview ? (
          <div style={{ textAlign: 'center' }}>
            <img src={preview.url} alt="" style={{ maxWidth: '100%', maxHeight: '62vh', borderRadius: 8 }} />
          </div>
        ) : (
          <>
            {/* 写真は画面におさまる大きさ（縦長でも、下のボタンまで見える） */}
            <div style={{ textAlign: 'center' }}>
              <div
                ref={boxRef}
                style={{ position: 'relative', display: 'inline-block', maxWidth: '100%', touchAction: 'none', userSelect: 'none', WebkitUserSelect: 'none', lineHeight: 0 }}
                onPointerDown={onDown}
                onPointerMove={onMove}
                onPointerUp={() => setDrag(null)}
                onPointerCancel={() => setDrag(null)}
              >
                <img
                  src={url}
                  alt=""
                  draggable={false}
                  style={{ maxWidth: '100%', maxHeight: '58vh', width: 'auto', height: 'auto', display: 'block', borderRadius: 4 }}
                  onLoad={(e) => {
                    const im = e.currentTarget
                    setSize({ w: im.naturalWidth, h: im.naturalHeight })
                    setQuad(defaultQuad(im.naturalWidth, im.naturalHeight))
                    setShown(im.clientWidth)
                  }}
                />
                {pts && (
                  <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none' }}>
                    <polygon points={pts.map((p) => `${p.x},${p.y}`).join(' ')} fill="rgba(255,255,255,0.12)" stroke="#ff2d55" strokeWidth={2} />
                    {pts.map((p, i) => (
                      <g key={i}>
                        <circle cx={p.x} cy={p.y} r={HANDLE} fill={sel === i ? 'rgba(255,45,85,0.35)' : 'rgba(255,45,85,0.14)'} stroke="#ff2d55" strokeWidth={sel === i ? 3.5 : 2} />
                        <circle cx={p.x} cy={p.y} r={2.5} fill="#ff2d55" />
                        <text
                          x={p.x + (i === 1 || i === 2 ? HANDLE + 4 : -HANDLE - 4)}
                          y={p.y + (i < 2 ? -HANDLE : HANDLE + 12)}
                          fontSize={12}
                          fontWeight={700}
                          fill="#ff2d55"
                          textAnchor={i === 1 || i === 2 ? 'start' : 'end'}
                          style={{ paintOrder: 'stroke', stroke: '#fff', strokeWidth: 3 }}
                        >
                          {NAMES[i]}
                        </text>
                      </g>
                    ))}
                  </svg>
                )}
                {drag !== null && pts && size && (
                  <div
                    aria-hidden
                    style={{
                      position: 'absolute',
                      pointerEvents: 'none',
                      // 指で隠れないよう、点が上半分なら下に、下半分なら上に（左右も同じ）出す
                      top: pts[drag].y < shownH * 0.5 ? undefined : 8,
                      bottom: pts[drag].y < shownH * 0.5 ? 8 : undefined,
                      left: pts[drag].x < shown * 0.5 ? undefined : 8,
                      right: pts[drag].x < shown * 0.5 ? 8 : undefined,
                      width: LOUPE,
                      height: LOUPE,
                      borderRadius: '50%',
                      border: '3px solid #fff',
                      boxShadow: '0 0 0 1px rgba(0,0,0,.4), 0 4px 12px rgba(0,0,0,.35)',
                      backgroundImage: `url(${url})`,
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: `${shown * ZOOM}px ${shownH * ZOOM}px`,
                      backgroundPosition: `${-(pts[drag].x * ZOOM - LOUPE / 2)}px ${-(pts[drag].y * ZOOM - LOUPE / 2)}px`,
                    }}
                  >
                    <div style={{ position: 'absolute', left: '50%', top: '50%', width: 12, height: 12, margin: -6, borderRadius: '50%', border: '2px solid #ff2d55' }} />
                  </div>
                )}
              </div>
            </div>

            {/* 微調整：選んでいる角を、1 ピクセルずつ（長押しで連続） */}
            <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'space-between' }}>
              <div className="small">
                <div style={{ fontWeight: 700 }}>{NAMES[sel]}の点を微調整</div>
                <div className="xs muted">点を押すと切り替わります</div>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                {arrow('左', -1, 0, IconArrowLeft)}
                {arrow('上', 0, -1, IconArrowUp)}
                {arrow('下', 0, 1, IconArrowDown)}
                {arrow('右', 1, 0, IconArrowRight)}
              </div>
            </div>
          </>
        )}

        {error && (
          <p className="small" role="alert" style={{ color: 'var(--danger)', marginTop: 8 }}>
            {error}
          </p>
        )}
        <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
          {preview ? (
            <>
              <button className="btn" style={{ flex: 1 }} disabled={busy} onClick={() => setPreview(null)}>
                もどって直す
              </button>
              <button className="btn primary" style={{ flex: 1 }} disabled={busy} onClick={save}>
                {busy ? '保存中…' : 'この画像で登録'}
              </button>
            </>
          ) : (
            <>
              <button className="btn" style={{ flex: 1 }} disabled={busy} onClick={onClose}>
                やめる
              </button>
              <button className="btn primary" style={{ flex: 1 }} disabled={busy || !quad} onClick={crop}>
                {busy ? '切り取り中…' : '切り取る'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>,
    document.body,
  )
}
