import { useRef, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { IconDatabaseImport, IconDownload, IconFileImport, IconPhotoUp, IconRestore } from '@tabler/icons-react'
import { db, getSetting } from '../lib/db'
import { exportBackup, markBackedUp, restoreBackup, saveFile } from '../lib/backup'
import { importCsv } from '../lib/csv'
import { importImages } from '../lib/imageImport'
import { TopBar } from '../components/ui'

const SEED_BASE = `${import.meta.env.BASE_URL}seed/`

function formatDate(ms: number): string {
  const d = new Date(ms)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}

/** S-09 設定 */
export default function Settings() {
  const lastBackupAt = useLiveQuery(() => getSetting<number>('lastBackupAt'))
  const counts = useLiveQuery(async () => ({ collections: await db.collections.count(), cards: await db.cards.count() }))
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  // 作ったバックアップ。iPhone の「保存」はタップの直後でないと開けないので、作るのと保存を 2 回のタップに分ける
  const [backupFile, setBackupFile] = useState<File | null>(null)
  const restoreRef = useRef<HTMLInputElement>(null)
  const csvRef = useRef<HTMLInputElement>(null)
  const imagesRef = useRef<HTMLInputElement>(null)

  const run = async (fn: () => Promise<string>) => {
    setBusy(true)
    setMessage('')
    try {
      setMessage(await fn())
    } catch (e) {
      if ((e as Error).name !== 'AbortError') setMessage(`失敗しました：${(e as Error).message}`)
    } finally {
      setBusy(false)
    }
  }

  const importSeed = () =>
    run(async () => {
      const [cols, cards] = await Promise.all(
        ['collections.csv', 'cards.csv'].map((f) =>
          fetch(SEED_BASE + f).then((r) => {
            if (!r.ok) throw new Error('初期データが見つかりません')
            return r.text()
          }),
        ),
      )
      const r = await importCsv(cols, cards)
      return `コレクション ${r.addedCollections} 件、カード ${r.addedCards} 枚を追加しました（すでにある ${r.skippedCards} 枚はそのまま）`
    })

  const importFiles = (files: FileList | null) =>
    run(async () => {
      const list = [...(files ?? [])]
      const cols = list.find((f) => f.name.includes('collection'))
      const cards = list.find((f) => f.name.includes('card'))
      if (!cols || !cards) throw new Error('collections.csv と cards.csv の 2 つを選んでください')
      const r = await importCsv(await cols.text(), await cards.text())
      return `コレクション ${r.addedCollections} 件、カード ${r.addedCards} 枚を追加しました（すでにある ${r.skippedCards} 枚はそのまま）`
    })

  return (
    <div className="page">
      <TopBar title="設定" />

      <div className="section-title">バックアップ</div>
      <div className="panel stack">
        <div className="small muted">
          最後のバックアップ：{lastBackupAt ? formatDate(lastBackupAt) : 'まだありません'}
        </div>
        {backupFile ? (
          <button
            className="btn primary block"
            disabled={busy}
            onClick={() =>
              run(async () => {
                await saveFile(backupFile)
                await markBackedUp()
                setBackupFile(null)
                return 'バックアップを保存しました'
              })
            }
          >
            <IconDownload size={20} aria-hidden />
            「ファイル」に保存する（{Math.max(1, Math.round(backupFile.size / 1024 / 1024))}MB）
          </button>
        ) : (
          <button
            className="btn primary block"
            disabled={busy}
            onClick={() =>
              run(async () => {
                setMessage('バックアップを作っています…')
                const { file, skipped } = await exportBackup()
                setBackupFile(file)
                return (
                  'できました。上の保存ボタンを押して「ファイル」アプリに保存してください' +
                  (skipped ? `（読み込めなかった画像 ${skipped} 枚は入っていません。記録はすべて入っています）` : '')
                )
              })
            }
          >
            <IconDownload size={20} aria-hidden />
            バックアップを書き出す
          </button>
        )}
        <div className="xs muted">
          画像の ZIP から取り込んだ画像は入りません（戻したあと、画像の ZIP を取り込み直してください）。自分で登録した画像は入ります。
        </div>
        <button className="btn block" disabled={busy} onClick={() => restoreRef.current?.click()}>
          <IconRestore size={20} aria-hidden />
          バックアップから戻す
        </button>
        <input
          ref={restoreRef}
          type="file"
          accept=".zip,application/zip"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0]
            e.target.value = ''
            if (!f) return
            if (!confirm('今のデータはすべてバックアップの内容に置き換わります。よろしいですか？')) return
            run(async () => {
              await restoreBackup(f)
              return 'バックアップから戻しました。画像は「画像をまとめて取り込む」で ZIP を取り込み直してください'
            })
          }}
        />
      </div>

      <div className="section-title">データの取り込み</div>
      <div className="panel stack">
        <div className="small muted">
          いまの登録数：コレクション {counts?.collections ?? 0} 件、カード {counts?.cards ?? 0} 枚
        </div>
        <button className="btn block" disabled={busy} onClick={importSeed}>
          <IconDatabaseImport size={20} aria-hidden />
          初期データを取り込む
        </button>
        <button className="btn block" disabled={busy} onClick={() => csvRef.current?.click()}>
          <IconFileImport size={20} aria-hidden />
          CSV ファイルから取り込む
        </button>
        <input
          ref={csvRef}
          type="file"
          accept=".csv,text/csv"
          multiple
          hidden
          onChange={(e) => {
            importFiles(e.target.files)
            e.target.value = ''
          }}
        />
        <button className="btn block" disabled={busy} onClick={() => imagesRef.current?.click()}>
          <IconPhotoUp size={20} aria-hidden />
          画像をまとめて取り込む（ZIP）
        </button>
        <input
          ref={imagesRef}
          type="file"
          accept=".zip,application/zip"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0]
            e.target.value = ''
            if (!f) return
            run(async () => {
              const r = await importImages(f, (done, total) => setMessage(`画像を取り込み中… ${done} / ${total}`))
              const miss = r.unmatched.length
              return `画像 ${r.matched} 枚を取り込みました` + (miss ? `（対応するカードがなかった ${miss} 枚：${r.unmatched.slice(0, 5).join('、')}${miss > 5 ? ' など' : ''}）` : '')
            })
          }}
        />
        <div className="xs muted">すでにあるカードの状態は上書きしません。画像は同じカードの画像を置き換えます。</div>
      </div>

      {message && (
        <p className="small" role="status" style={{ marginTop: 16 }}>
          {message}
        </p>
      )}
    </div>
  )
}
