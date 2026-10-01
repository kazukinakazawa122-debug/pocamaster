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

export async function makeImage(file: Blob): Promise<{ full: Blob; thumb: Blob }> {
  const [full, thumb] = await Promise.all([resize(file, 1200, 0.85), resize(file, 400, 0.8)])
  return { full, thumb }
}
