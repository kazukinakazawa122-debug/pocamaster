// 画像を縮めて保存する（03_データ設計 2.4）
async function resize(file: Blob, maxSide: number, quality: number): Promise<Blob> {
  const bmp = await createImageBitmap(file)
  const scale = Math.min(1, maxSide / Math.max(bmp.width, bmp.height))
  const w = Math.round(bmp.width * scale)
  const h = Math.round(bmp.height * scale)
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  canvas.getContext('2d')!.drawImage(bmp, 0, 0, w, h)
  bmp.close()
  return new Promise((resolve, reject) =>
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('画像を変換できませんでした'))), 'image/jpeg', quality),
  )
}

/** 画質を上げる方針（本人、2026-10-02）：大きい画像 1200→1600px・0.85→0.9、一覧用 400→600px・0.8→0.85（実物の写真をきれいに残す） */
export async function makeImage(file: Blob): Promise<{ full: Blob; thumb: Blob }> {
  const [full, thumb] = await Promise.all([resize(file, 1600, 0.9), resize(file, 600, 0.85)])
  return { full, thumb }
}
