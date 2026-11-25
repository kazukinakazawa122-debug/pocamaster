import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// 字体は Google Fonts から（まとめる道具が外のファイルを読めないので、ここで足す）
const f = document.createElement('link')
f.rel = 'stylesheet'
f.href = 'https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700&family=Zen+Maru+Gothic:wght@700&display=swap'
document.head.appendChild(f)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
