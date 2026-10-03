/**
 * 写真の中のカードの四隅から、まっすぐなカードの画像を切り出す（遠近補正。2026-10-03、アプリの改善 44.【2】）。
 * 斜めから撮った写真・隣のカードとぴったり並んだ写真でも、四隅を合わせれば、カードの全体がまっすぐに取れる。
 * 画面に依存しない関数だけ（canvas を使わない）にして、自動テストで確かめる
 */
export interface Point {
  x: number
  y: number
}
/** 左上・右上・右下・左下の順 */
export type Quad = [Point, Point, Point, Point]

export interface Rgba {
  width: number
  height: number
  data: Uint8ClampedArray
}

/** フォトカードの縦横の比（縦 ÷ 横）。標準のカードは 55×85mm ほど */
export const CARD_RATIO = 1.55

/** 八元一次方程式 A·c = b を掃き出し法で解く */
function solve(A: number[][], b: number[]): number[] {
  const n = b.length
  const M = A.map((row, i) => [...row, b[i]])
  for (let i = 0; i < n; i++) {
    let p = i
    for (let r = i + 1; r < n; r++) if (Math.abs(M[r][i]) > Math.abs(M[p][i])) p = r
    if (Math.abs(M[p][i]) < 1e-12) throw new Error('四隅が一直線に近く、切り出せません')
    ;[M[i], M[p]] = [M[p], M[i]]
    for (let r = 0; r < n; r++) {
      if (r === i) continue
      const f = M[r][i] / M[i][i]
      for (let c = i; c <= n; c++) M[r][c] -= f * M[i][c]
    }
  }
  return M.map((row, i) => row[n] / row[i])
}

/** 出力の長方形（0,0）-（w,h）の点を、写真の四隅の中の点へ移す遠近変換（8 つの係数） */
export function homography(quad: Quad, w: number, h: number): number[] {
  const dst = [[0, 0], [w, 0], [w, h], [0, h]]
  const A: number[][] = []
  const b: number[] = []
  dst.forEach(([x, y], i) => {
    const { x: u, y: v } = quad[i]
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y])
    b.push(u)
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y])
    b.push(v)
  })
  return solve(A, b)
}

/** 四隅（左上・右上・右下・左下）の長さの平均から、出力の大きさを決める（縦横の比はカードの比 CARD_RATIO。長い辺は maxSide まで） */
export function outputSize(quad: Quad, maxSide = 1600): { width: number; height: number } {
  const d = (a: Point, b: Point) => Math.hypot(a.x - b.x, a.y - b.y)
  const w = (d(quad[0], quad[1]) + d(quad[3], quad[2])) / 2
  const h = (d(quad[0], quad[3]) + d(quad[1], quad[2])) / 2
  // 写真の縦横が逆（横向きのカード）なら、横長に出す
  const landscape = w > h * 1.1
  let width = w
  let height = landscape ? width / CARD_RATIO : width * CARD_RATIO
  const k = Math.min(1, maxSide / Math.max(width, height))
  width *= k
  height *= k
  return { width: Math.max(2, Math.round(width)), height: Math.max(2, Math.round(height)) }
}

/** 写真（RGBA）から四隅の中を切り出し、width×height のまっすぐな画像にする（双一次補間） */
export function warp(src: Rgba, quad: Quad, width: number, height: number): Rgba {
  const c = homography(quad, width, height)
  const out = new Uint8ClampedArray(width * height * 4)
  const { data, width: sw, height: sh } = src
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      // ピクセルの中心で変換する
      const px = x + 0.5
      const py = y + 0.5
      const den = c[6] * px + c[7] * py + 1
      const u = (c[0] * px + c[1] * py + c[2]) / den - 0.5
      const v = (c[3] * px + c[4] * py + c[5]) / den - 0.5
      const x0 = Math.floor(u)
      const y0 = Math.floor(v)
      const fx = u - x0
      const fy = v - y0
      const o = (y * width + x) * 4
      for (let ch = 0; ch < 4; ch++) {
        const at = (xx: number, yy: number) => data[(Math.min(sh - 1, Math.max(0, yy)) * sw + Math.min(sw - 1, Math.max(0, xx))) * 4 + ch]
        out[o + ch] =
          at(x0, y0) * (1 - fx) * (1 - fy) + at(x0 + 1, y0) * fx * (1 - fy) + at(x0, y0 + 1) * (1 - fx) * fy + at(x0 + 1, y0 + 1) * fx * fy
      }
    }
  }
  return { width, height, data: out }
}

/** 写真いっぱいに、まわりを少し空けた四隅（切り取りを始めるときの初期の位置） */
export function defaultQuad(width: number, height: number): Quad {
  // カードの比で、写真の中央に置く
  let w = width * 0.62
  let h = w * CARD_RATIO
  if (h > height * 0.8) {
    h = height * 0.8
    w = h / CARD_RATIO
  }
  const x0 = (width - w) / 2
  const y0 = (height - h) / 2
  return [
    { x: x0, y: y0 },
    { x: x0 + w, y: y0 },
    { x: x0 + w, y: y0 + h },
    { x: x0, y: y0 + h },
  ]
}
