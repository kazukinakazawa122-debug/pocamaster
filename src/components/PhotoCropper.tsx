import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { makeImage } from '../lib/image'
import { defaultQuad, outputSize, warp, type Point, type Quad } from '../lib/warp'

interface Props {
  file: File
  /** 切り取ったカードの画像（大きい画像と一覧用）を渡す。保存は呼んだ側で行う */
  onDone: (img: { full: Blob; thumb: Blob }) => Promise<void>
  onClose: () => void
}

const LOUPE = 104
const ZOOM = 3
const HANDLE = 22 // 画面上の点の大きさ（px）

/**
 * 実物のカードの写真から、カードの四隅を合わせて、まっすぐな 1 枚の画像を切り取る（2026-10-03、アプリの改善 44.【2】）。
 * フリマの出品写真・自分で撮った写真・6 枚並びの写真のどれでも使える。四隅の点を指でドラッグして合わせ、「切り取る」で確かめて登録する。
 * ドラッグ中は、点のまわりを拡大して見せる（指で隠れないように）
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

  const move = (i: number, e: React.PointerEvent) => {
    const el = boxRef.current
    if (!el || !size || !quad) return
    const r = el.getBoundingClientRect()
    const x = Math.min(size.w, Math.max(0, (e.clientX - r.left) / scale))
    const y = Math.min(size.h, Math.max(0, (e.clientY - r.top) / scale))
    setQuad(quad.map((p, k) => (k === i ? { x, y } : p)) as Quad)
  }

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

  const pts: Point[] | undefined = quad?.map((p) => ({ x: p.x * scale, y: p.y * scale }))
  const shownH = size ? shown * (size.h / size.w) : 0

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
            カードの四隅の点を、指でドラッグして合わせてください。ななめに撮った写真でも、まっすぐに直します。
          </div>
        )}

        {preview ? (
          <div style={{ textAlign: 'center' }}>
            <img src={preview.url} alt="" style={{ maxWidth: '100%', maxHeight: '62vh', borderRadius: 8 }} />
          </div>
        ) : (
          <div ref={boxRef} style={{ position: 'relative', touchAction: 'none', userSelect: 'none', WebkitUserSelect: 'none' }}>
            <img
              src={url}
              alt=""
              draggable={false}
              style={{ width: '100%', display: 'block', borderRadius: 4 }}
              onLoad={(e) => {
                const im = e.currentTarget
                setSize({ w: im.naturalWidth, h: im.naturalHeight })
                setQuad(defaultQuad(im.naturalWidth, im.naturalHeight))
              }}
            />
            {pts && (
              <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible' }}>
                <polygon points={pts.map((p) => `${p.x},${p.y}`).join(' ')} fill="rgba(255,255,255,0.12)" stroke="#ff2d55" strokeWidth={2.5} />
                {pts.map((p, i) => (
                  <g key={i}>
                    <circle cx={p.x} cy={p.y} r={HANDLE} fill="rgba(255,45,85,0.18)" stroke="#ff2d55" strokeWidth={2.5} />
                    <circle cx={p.x} cy={p.y} r={3} fill="#ff2d55" />
                    {/* 触れる範囲は見た目より大きく（指で押しやすいように） */}
                    <circle
                      cx={p.x}
                      cy={p.y}
                      r={HANDLE + 14}
                      fill="transparent"
                      style={{ touchAction: 'none', cursor: 'grab' }}
                      data-testid={`corner-${i}`}
                      onPointerDown={(e) => {
                        e.currentTarget.setPointerCapture(e.pointerId)
                        setDrag(i)
                        move(i, e)
                      }}
                      onPointerMove={(e) => drag === i && move(i, e)}
                      onPointerUp={() => setDrag(null)}
                      onPointerCancel={() => setDrag(null)}
                    />
                  </g>
                ))}
              </svg>
            )}
            {drag !== null && pts && size && (
              <div
                aria-hidden
                style={{
                  position: 'absolute',
                  // 指で隠れないよう、点が上半分なら下に、下半分なら上に出す
                  top: pts[drag].y < shownH * 0.5 ? undefined : 8,
                  bottom: pts[drag].y < shownH * 0.5 ? 8 : undefined,
                  left: 8,
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
                <div style={{ position: 'absolute', left: '50%', top: '50%', width: 10, height: 10, margin: -5, borderRadius: '50%', border: '2px solid #ff2d55' }} />
              </div>
            )}
          </div>
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
