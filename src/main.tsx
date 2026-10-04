import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { registerSW } from 'virtual:pwa-register'
import App from './App'
import '@fontsource/fredoka/latin-600.css'
import './styles.css'

// iPhone がデータを勝手に消さないようにお願いする（対応していない環境では何もしない）
navigator.storage?.persist?.()

// 保存に失敗したのに、何も出ないままにしない（iPhone の空き容量がいっぱいのとき、カードの切り替えや画像の保存が黙って失敗する）。
// 画面ごとに伝えていない保存の失敗を、1 回だけ知らせる
let warnedSave = false
window.addEventListener('unhandledrejection', (e) => {
  const err = e.reason as { name?: string; inner?: { name?: string } } | undefined
  const name = err?.name ?? err?.inner?.name ?? ''
  if (warnedSave || !/QuotaExceeded|DatabaseClosed|VersionError|UnknownError|AbortError/.test(name)) return
  warnedSave = true
  alert('保存できませんでした。iPhone の空き容量が足りないか、アプリを開き直す必要があるかもしれません。バックアップを取ってから、アプリを開き直してください。')
})

// 新しい版を公開したら、アプリに戻ってきたときに確かめ、あれば自動で切り替える
// （ホーム画面のアプリは閉じずに裏に残ることが多く、そのままだと古い版を使い続けるため）
registerSW({
  immediate: true,
  onRegisteredSW(_url, registration) {
    if (!registration) return
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') registration.update()
    })
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
)
