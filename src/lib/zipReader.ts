import JSZip from 'jszip'

/**
 * ZIP の中のファイルを読む（2026-10-14、使用感の調査 52. の 4）。
 * 全部入りの画像 ZIP（約 300MB）を JSZip で開くと、ZIP 全体を一度にメモリへ読み込む（パソコンでも最大 約 1.1GB。iPhone では落ちるおそれ）。
 * そこで、終わりにある「中のファイルの一覧」（中央ディレクトリ）だけを先に読み、中身は要るときに 1 つずつ切り出して読む（Blob.slice）。
 * 対応していない形（ZIP64・暗号化・知らない圧縮の方式など）のときは、これまでどおり JSZip で全部読み込む
 */
export interface ZipReader {
  /** true＝1 つずつ切り出して読んでいる。false＝JSZip で全部読み込んだ（読めない形の ZIP） */
  lazy: boolean
  /** 中のファイルの名前（フォルダは除く） */
  names: string[]
  /** ファイルの中身（メモリに写したもの。元の ZIP を参照しない）。なければ undefined */
  bytes(name: string): Promise<ArrayBuffer | undefined>
  /** ファイルの中身を文字として（UTF-8）。なければ undefined */
  text(name: string): Promise<string | undefined>
}

interface Entry {
  method: number
  compressedSize: number
  offset: number
  nameLen: number
  extraLen: number
}

const EOCD = 0x06054b50 // 終わりの記録
const ZIP64_LOCATOR = 0x07064b50
const CENTRAL = 0x02014b50 // 一覧の 1 件
const LOCAL = 0x04034b50 // 中身の前の記録
const MAX = 0xffffffff
/** ファイルからまとめて読む大きさ（画像の大きいもの 1 枚より大きく、メモリには小さい） */
const WINDOW = 4 * 1024 * 1024

/** この読み方では読めない形（JSZip で読み直す） */
class Unsupported extends Error {}

async function view(file: Blob, start: number, end: number): Promise<DataView> {
  return new DataView(await file.slice(start, end).arrayBuffer())
}

async function openLazy(file: Blob): Promise<ZipReader> {
  // 1. 終わりの記録を、後ろから探す（後ろにコメントがあると最大 65,535 バイトずれる）
  const tailLen = Math.min(file.size, 22 + 0xffff)
  const tail = await view(file, file.size - tailLen, file.size)
  let at = -1
  for (let i = tail.byteLength - 22; i >= 0; i--) {
    if (tail.getUint32(i, true) === EOCD) {
      at = i
      break
    }
  }
  if (at < 0) throw new Unsupported('ZIP の終わりの記録がありません')
  if (at >= 20 && tail.getUint32(at - 20, true) === ZIP64_LOCATOR) throw new Unsupported('ZIP64')
  const count = tail.getUint16(at + 10, true)
  const cdSize = tail.getUint32(at + 12, true)
  const cdOffset = tail.getUint32(at + 16, true)
  if (count === 0xffff || cdSize === MAX || cdOffset === MAX || cdOffset + cdSize > file.size) throw new Unsupported('ZIP64 か、壊れた ZIP')

  // 2. 中のファイルの一覧（1 万件で約 1MB）
  const cd = await view(file, cdOffset, cdOffset + cdSize)
  const decoder = new TextDecoder()
  const entries = new Map<string, Entry>()
  let p = 0
  for (let k = 0; k < count; k++) {
    if (p + 46 > cd.byteLength || cd.getUint32(p, true) !== CENTRAL) throw new Unsupported('一覧が読めません')
    const flags = cd.getUint16(p + 8, true)
    const method = cd.getUint16(p + 10, true)
    const compressedSize = cd.getUint32(p + 20, true)
    const size = cd.getUint32(p + 24, true)
    const nameLen = cd.getUint16(p + 28, true)
    const extraLen = cd.getUint16(p + 30, true)
    const commentLen = cd.getUint16(p + 32, true)
    const offset = cd.getUint32(p + 42, true)
    const name = decoder.decode(new Uint8Array(cd.buffer, cd.byteOffset + p + 46, nameLen))
    if (compressedSize === MAX || size === MAX || offset === MAX) throw new Unsupported('ZIP64')
    if (flags & 1) throw new Unsupported('暗号化')
    if (method !== 0 && !(method === 8 && typeof DecompressionStream !== 'undefined')) throw new Unsupported('知らない圧縮の方式')
    if (!name.endsWith('/')) entries.set(name, { method, compressedSize, offset, nameLen, extraLen })
    p += 46 + nameLen + extraLen + commentLen
  }

  // ファイルから読むのは、まとめて WINDOW ずつ（その中から 1 つずつ切り出す）。画像の ZIP は、取り込む順に中身が並んでいるので、
  // 続けて読むとほとんどがすでに読んだ範囲に入る（1 つずつファイルから読むと、全部入りの取り込みが 66 秒 → 121 秒に遅くなった）
  let win: { start: number; buf: ArrayBuffer } | null = null
  const range = async (start: number, end: number): Promise<Uint8Array> => {
    let w = win
    if (!w || start < w.start || end > w.start + w.buf.byteLength) {
      w = { start, buf: await file.slice(start, Math.min(file.size, Math.max(end, start + WINDOW))).arrayBuffer() }
      win = w
    }
    return new Uint8Array(w.buf, start - w.start, Math.min(end, w.start + w.buf.byteLength) - start)
  }

  const bytes = async (name: string): Promise<ArrayBuffer | undefined> => {
    const e = entries.get(name)
    if (!e) return undefined
    // 中身の前の記録（30 バイト＋名前＋追加の欄）と中身を一緒に読む。追加の欄の長さは一覧と違うことがあるので、少し多めに読み、足りなければ読み直す
    let u = await range(e.offset, Math.min(file.size, e.offset + 30 + e.nameLen + e.extraLen + 1024 + e.compressedSize))
    const v = new DataView(u.buffer, u.byteOffset, u.byteLength)
    if (v.byteLength < 30 || v.getUint32(0, true) !== LOCAL) throw new Error('ZIP の中身が読めません')
    const start = 30 + v.getUint16(26, true) + v.getUint16(28, true)
    if (start + e.compressedSize > u.byteLength) u = await range(e.offset, e.offset + start + e.compressedSize)
    if (start + e.compressedSize > u.byteLength) throw new Error('ZIP の中身が途中で切れています')
    // 中身の部分だけを、新しい入れ物に写す（まとめて読んだ範囲を持ち続けない）
    const raw = u.slice(start, start + e.compressedSize).buffer as ArrayBuffer
    if (e.method === 0) return raw
    return new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer()
  }
  return {
    lazy: true,
    names: [...entries.keys()],
    bytes,
    text: async (name) => {
      const b = await bytes(name)
      return b && new TextDecoder().decode(b)
    },
  }
}

/** ZIP を開く。ふつうは 1 つずつ切り出して読む。読めない形なら JSZip で全部読み込む（これまでどおり） */
export async function openZip(file: Blob): Promise<ZipReader> {
  try {
    return await openLazy(file)
  } catch (e) {
    // 読めない形・記録の数字がおかしい ZIP は JSZip に任せる（ファイル自体が読めないときは、そのまま知らせる）
    if (!(e instanceof Unsupported || e instanceof RangeError)) throw e
  }
  const zip = await JSZip.loadAsync(file)
  return {
    lazy: false,
    names: Object.values(zip.files)
      .filter((f) => !f.dir)
      .map((f) => f.name),
    bytes: async (name) => zip.file(name)?.async('arraybuffer'),
    text: async (name) => zip.file(name)?.async('string'),
  }
}
