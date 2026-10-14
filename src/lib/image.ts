// 画像を縮めて保存する（03_データ設計 2.4）
async function toJpeg(bmp: ImageBitmap, maxSide: number, quality: number): Promise<Blob> {
  const scale = Math.min(1, maxSide / Math.max(bmp.width, bmp.height))
  const w = Math.round(bmp.width * scale)
  const h = Math.round(bmp.height * scale)
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  canvas.getContext('2d')!.drawImage(bmp, 0, 0, w, h)
  try {
    return await new Promise((resolve, reject) =>
      canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('画像を変換できませんでした'))), 'image/jpeg', quality),
    )
  } finally {
    // 使い終わった画用紙（canvas）はすぐ手放す。iPhone では canvas のメモリの合計に上限があり、続けて何十枚も作ると作れなくなることがある（2026-10-14）
    canvas.width = 0
    canvas.height = 0
  }
}

/**
 * 画質を上げる方針（本人、2026-10-02）：大きい画像 1200→1600px・0.85→0.9、一覧用 400→600px・0.8→0.85（実物の写真をきれいに残す）。
 * 写真の読み込み（展開）は 1 回だけにして、大きい画像と一覧用を順に作る（前は 2 回展開していた。12MP の写真は 1 回で約 48MB。2026-10-14）
 */
export async function makeImage(file: Blob): Promise<{ full: Blob; thumb: Blob }> {
  let bmp: ImageBitmap
  try {
    bmp = await createImageBitmap(file)
  } catch {
    // ブラウザの英語の知らせ（The source image could not be decoded など）をそのまま出さない
    throw new Error('写真を読み込めませんでした。別の写真を選んでください')
  }
  try {
    const full = await toJpeg(bmp, 1600, 0.9)
    const thumb = await toJpeg(bmp, 600, 0.85)
    return { full, thumb }
  } finally {
    bmp.close()
  }
}
