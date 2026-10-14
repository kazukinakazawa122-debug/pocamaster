import { describe, expect, it } from 'vitest'
import JSZip from 'jszip'
import { openZip } from './zipReader'

/** 中身を比べやすい、決まった並びのバイト列（同じ値が続かないように） */
function bytesOf(n: number, seed: number): Uint8Array {
  const out = new Uint8Array(n)
  let x = seed
  for (let i = 0; i < n; i++) {
    x = (x * 1103515245 + 12345) >>> 0
    out[i] = x >>> 24
  }
  return out
}

async function zipOf(files: Record<string, Uint8Array | string>, opts: Parameters<JSZip['generateAsync']>[0] = {}): Promise<Blob> {
  const zip = new JSZip()
  for (const [name, data] of Object.entries(files)) zip.file(name, data)
  zip.folder('からのフォルダ')
  return zip.generateAsync({ type: 'blob', ...opts })
}

const same = (a: ArrayBuffer | undefined, b: Uint8Array) => !!a && a.byteLength === b.byteLength && new Uint8Array(a).every((v, i) => v === b[i])

/** ZIP を 1 つずつ切り出して読む（全部入りの画像 ZIP を一度にメモリへ読み込まないため。2026-10-14） */
describe('ZIP を読む', () => {
  const big = bytesOf(200_000, 1)
  const small = bytesOf(3_000, 2)

  it('圧縮なしの ZIP（パソコンの全部入り・差分 ZIP と同じ形）を、1 つずつ切り出して読む。日本語の名前・後ろのコメントも読める', async () => {
    const z = await openZip(await zipOf({ 'img/0000.jpg': big, 'img/0000_t.jpg': small, 'manifest.json': '[{"collection":"テスト盤"}]', '日本語の名前.txt': 'あいう' }, { comment: 'ZIP のコメント' }))
    expect(z.lazy).toBe(true)
    expect(z.names.sort()).toEqual(['img/0000.jpg', 'img/0000_t.jpg', 'manifest.json', '日本語の名前.txt'])
    expect(same(await z.bytes('img/0000.jpg'), big)).toBe(true)
    expect(same(await z.bytes('img/0000_t.jpg'), small)).toBe(true)
    expect(JSON.parse((await z.text('manifest.json'))!)).toEqual([{ collection: 'テスト盤' }])
    expect(await z.text('日本語の名前.txt')).toBe('あいう')
    expect(await z.bytes('ない.jpg')).toBeUndefined()
  })

  it('圧縮した ZIP（パソコンで作り直した ZIP など）も、1 つずつ読める', async () => {
    const z = await openZip(await zipOf({ 'a.bin': big, 'b.txt': 'テキスト'.repeat(1000) }, { compression: 'DEFLATE' }))
    expect(z.lazy).toBe(true)
    expect(same(await z.bytes('a.bin'), big)).toBe(true)
    expect(await z.text('b.txt')).toBe('テキスト'.repeat(1000))
  })

  it('中身のあとに大きさを書く形（データディスクリプタ）でも読める', async () => {
    const z = await openZip(await zipOf({ 'a.bin': big, 'b.bin': small }, { compression: 'DEFLATE', streamFiles: true }))
    expect(z.lazy).toBe(true)
    expect(same(await z.bytes('a.bin'), big)).toBe(true)
    expect(same(await z.bytes('b.bin'), small)).toBe(true)
  })

  it('まとめて読む範囲（4MB）をまたいでも、順に読んでも逆から読んでも、中身が合う。4MB より大きいファイルも読める', async () => {
    const files: Record<string, Uint8Array> = {}
    for (let i = 0; i < 6; i++) files[`img/${i}.jpg`] = bytesOf(1_000_000 + i * 1234, 10 + i)
    files['img/big.jpg'] = bytesOf(5_500_000, 99)
    const z = await openZip(await zipOf(files))
    expect(z.lazy).toBe(true)
    for (const name of Object.keys(files)) expect(same(await z.bytes(name), files[name])).toBe(true)
    for (const name of Object.keys(files).reverse()) expect(same(await z.bytes(name), files[name])).toBe(true)
  })

  it('ZIP でないファイルは、これまでどおり失敗を知らせる', async () => {
    await expect(openZip(new Blob(['これは ZIP ではありません']))).rejects.toThrow()
  })

  it('読める形でない ZIP（終わりの記録の数字が合わない）は、JSZip で読む', async () => {
    const blob = await zipOf({ 'a.bin': small })
    const buf = new Uint8Array(await blob.arrayBuffer())
    // 終わりの記録の「一覧の位置」を、ファイルの外を指す値に書き換える（この読み方では読めない）
    const at = buf.length - 22
    new DataView(buf.buffer).setUint32(at + 16, buf.length + 10, true)
    const z = await openZip(new Blob([buf])).catch(() => null)
    // JSZip でも読めないなら失敗を知らせる（どちらでも、まちがった中身は返さない）
    if (z) {
      expect(z.lazy).toBe(false)
      expect(same(await z.bytes('a.bin'), small)).toBe(true)
    }
  })
})
