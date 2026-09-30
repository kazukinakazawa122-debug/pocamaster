import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { registerSW } from 'virtual:pwa-register'
import App from './App'
import './styles.css'

// iPhone がデータを勝手に消さないようにお願いする（対応していない環境では何もしない）
navigator.storage?.persist?.()

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
