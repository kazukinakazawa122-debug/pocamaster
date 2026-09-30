import { useEffect, useRef, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { IconCamera, IconDatabaseImport, IconDownload, IconFileImport, IconPhotoUp, IconRestore } from '@tabler/icons-react'
import { db, EMPTY_PROFILE, getSetting, newId, putSetting, type Profile } from '../lib/db'
import { makeImage } from '../lib/image'
import MemberPicker from '../components/MemberPicker'
import { exportBackup, markBackedUp, restoreBackup, saveFile } from '../lib/backup'
import { importCsv, removeObsolete } from '../lib/csv'
import { importImages } from '../lib/imageImport'
import { ProfileAvatar, TopBar } from '../components/ui'

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
      // 初期データからなくした枠を消す（ファイルがなければ何もしない）
      const removedCsv = await fetch(SEED_BASE + 'removed.csv').then((res) => (res.ok ? res.text() : ''))
      const removed = await removeObsolete(removedCsv)
      return (
        `コレクション ${r.addedCollections} 件、カード ${r.addedCards} 枚を追加しました（すでにある ${r.skippedCards} 枚はそのまま）` +
        (removed ? `。まちがっていた枠 ${removed} 枚を消しました` : '')
      )
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
      <TopBar title="設定" minive="mix" />

      <div className="section-title">プロフィール</div>
      <ProfileEditor />

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

/** 設定のいちばん上のプロフィール。変えたらすぐ保存する */
function ProfileEditor() {
  const [draft, setDraft] = useState<Profile | null>(null)
  const latest = useRef<Profile | null>(null)
  const photoRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    getSetting<Profile>('profile').then((p) => {
      latest.current = { ...EMPTY_PROFILE, ...p }
      setDraft(latest.current)
    })
  }, [])
  if (!draft) return <div className="panel small muted">読み込み中…</div>

  // 写真の変換中に文字を打っても消えないよう、いちばん新しい内容に変更点だけを重ねる
  const save = (patch: Partial<Profile>) => {
    latest.current = { ...latest.current!, ...patch }
    setDraft(latest.current)
    putSetting('profile', latest.current)
  }

  const setPhoto = async (file: File) => {
    const img = await makeImage(file)
    const id = newId()
    await db.images.add({ id, ...img })
    const old = latest.current?.imageId
    save({ imageId: id })
    if (old) await db.images.delete(old)
  }

  return (
    <div className="panel">
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
        <button type="button" className="icon-btn" aria-label="アイコンの写真を選ぶ" onClick={() => photoRef.current?.click()} style={{ position: 'relative' }}>
          <ProfileAvatar profile={draft} size={72} />
          <span
            style={{ position: 'absolute', right: -2, bottom: -2, width: 26, height: 26, borderRadius: '50%', background: 'var(--all)', color: 'var(--on-all)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <IconCamera size={15} aria-hidden />
          </span>
        </button>
        <input
          ref={photoRef}
          type="file"
          accept="image/*"
          hidden
          onChange={(e) => {
            const f = e.target.files?.[0]
            e.target.value = ''
            if (f) setPhoto(f)
          }}
        />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 19, fontWeight: 800, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {draft.name || <span className="muted">名前なし</span>}
          </div>
          {draft.bio && <div className="small muted" style={{ whiteSpace: 'pre-wrap' }}>{draft.bio}</div>}
        </div>
      </div>
      <label className="field">
        <span>名前（ニックネーム）</span>
        <input type="text" value={draft.name} maxLength={30} placeholder="ニックネームを入力" onChange={(e) => save({ name: e.target.value })} />
      </label>
      <div className="field">
        <span>推しメン（アイコンの枠がこの色になります）</span>
        <MemberPicker value={draft.biasIds} onChange={(biasIds) => save({ biasIds })} />
      </div>
      <label className="field" style={{ marginBottom: 0 }}>
        <span>ひとこと</span>
        <textarea value={draft.bio} maxLength={100} placeholder="例：ユジン推しの 2022 年からの DIVE です" onChange={(e) => save({ bio: e.target.value })} />
      </label>
    </div>
  )
}
