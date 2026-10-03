import { describe, expect, it } from 'vitest'
import { CARD_RATIO, defaultQuad, homography, nearestCorner, nudge, outputSize, warp, type Quad, type Rgba } from './warp'

/** 小さな写真を作る：座標に比例する色（赤＝x、緑＝y）にして、どこから取ったか読めるようにする */
function gradient(w: number, h: number): Rgba {
  const data = new Uint8ClampedArray(w * h * 4)
  for (let y = 0; y < h; y++)
    for (let x = 0; x < w; x++) {
      const o = (y * w + x) * 4
      data[o] = Math.round((x / (w - 1)) * 255)
      data[o + 1] = Math.round((y / (h - 1)) * 255)
      data[o + 2] = 0
      data[o + 3] = 255
    }
  return { width: w, height: h, data }
}
const px = (img: Rgba, x: number, y: number) => [...img.data.slice((y * img.width + x) * 4, (y * img.width + x) * 4 + 3)]

describe('遠近補正の切り出し', () => {
  it('写真全体を四隅にすると、同じ画像が返る', () => {
    const src = gradient(40, 60)
    const q: Quad = [{ x: 0, y: 0 }, { x: 40, y: 0 }, { x: 40, y: 60 }, { x: 0, y: 60 }]
    const out = warp(src, q, 40, 60)
    for (const [x, y] of [[0, 0], [10, 20], [39, 59], [25, 3]]) {
      const a = px(src, x, y)
      const b = px(out, x, y)
      expect(Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1])).toBeLessThanOrEqual(2)
    }
  })

  it('長方形の一部を切り出すと、その部分だけが拡大して返る', () => {
    const src = gradient(100, 100)
    // 左上の 1/4（x 0〜50、y 0〜50）を 50×50 に
    const q: Quad = [{ x: 0, y: 0 }, { x: 50, y: 0 }, { x: 50, y: 50 }, { x: 0, y: 50 }]
    const out = warp(src, q, 50, 50)
    // 出力の右下は、元の (50, 50) あたり＝赤・緑とも約 50%
    const [r, g] = px(out, 49, 49)
    expect(r).toBeGreaterThan(110)
    expect(r).toBeLessThan(140)
    expect(g).toBeGreaterThan(110)
    expect(g).toBeLessThan(140)
  })

  it('斜めの四隅（台形）でも、出力の四隅が写真の四隅の色になる', () => {
    const src = gradient(200, 300)
    // 上が狭く下が広い台形（斜めから撮ったカード）
    const q: Quad = [{ x: 60, y: 40 }, { x: 140, y: 40 }, { x: 170, y: 250 }, { x: 30, y: 250 }]
    const out = warp(src, q, 80, 124)
    const near = (a: number[], x: number, y: number) => {
      expect(Math.abs(a[0] - (x / 199) * 255)).toBeLessThan(8)
      expect(Math.abs(a[1] - (y / 299) * 255)).toBeLessThan(8)
    }
    near(px(out, 0, 0), 60, 40)
    near(px(out, 79, 0), 140, 40)
    near(px(out, 79, 123), 170, 250)
    near(px(out, 0, 123), 30, 250)
  })

  it('四隅が一直線に並ぶと、切り出せないと伝える', () => {
    const q: Quad = [{ x: 0, y: 0 }, { x: 10, y: 10 }, { x: 20, y: 20 }, { x: 30, y: 30 }]
    expect(() => homography(q, 10, 10)).toThrow('一直線')
  })

  it('出力の大きさはカードの縦横の比になり、長い辺は上限までに収める', () => {
    const q: Quad = [{ x: 0, y: 0 }, { x: 400, y: 0 }, { x: 400, y: 620 }, { x: 0, y: 620 }]
    const s = outputSize(q)
    expect(s.width).toBe(400)
    expect(s.height).toBe(Math.round(400 * CARD_RATIO))
    const big = outputSize([{ x: 0, y: 0 }, { x: 3000, y: 0 }, { x: 3000, y: 4650 }, { x: 0, y: 4650 }], 1600)
    expect(Math.max(big.width, big.height)).toBe(1600)
  })

  it('初期の四隅は、写真の中に収まる', () => {
    for (const [w, h] of [[1284, 2778], [4000, 3000], [500, 500]]) {
      for (const p of defaultQuad(w, h)) {
        expect(p.x).toBeGreaterThanOrEqual(0)
        expect(p.x).toBeLessThanOrEqual(w)
        expect(p.y).toBeGreaterThanOrEqual(0)
        expect(p.y).toBeLessThanOrEqual(h)
      }
    }
  })

  it('押した位置にいちばん近い角を選ぶ（遠すぎれば選ばない）', () => {
    const pts = [{ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 100, y: 150 }, { x: 0, y: 150 }]
    expect(nearestCorner(pts, { x: 10, y: 8 }, 60)).toBe(0)
    expect(nearestCorner(pts, { x: 95, y: 140 }, 60)).toBe(2)
    expect(nearestCorner(pts, { x: 50, y: 75 }, 60)).toBeNull() // 真ん中は、どの角からも遠い
    // 近い 2 つの角の間なら、近いほう
    expect(nearestCorner([{ x: 0, y: 0 }, { x: 30, y: 0 }], { x: 20, y: 5 }, 60)).toBe(1)
  })

  it('角を動かす（写真の外には出さない）', () => {
    const q = defaultQuad(100, 150)
    const moved = nudge(q, 0, -1000, -1000, 100, 150)
    expect(moved[0]).toEqual({ x: 0, y: 0 })
    expect(moved[1]).toEqual(q[1]) // ほかの角は動かない
    expect(nudge(q, 2, 1, 2, 100, 150)[2]).toEqual({ x: q[2].x + 1, y: q[2].y + 2 })
  })
})
