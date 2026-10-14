import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// 公開のとき（GitHub Actions）は、公開する commit の番号が GITHUB_SHA に入っている（Node の型は入れていないので、型を付けずに読む）
const env = (globalThis as { process?: { env: Record<string, string | undefined> } }).process?.env ?? {}

// GitHub Pages ではリポジトリ名のパス（/pocamaster/）の下に置かれる
export default defineConfig({
  base: '/pocamaster/',
  // アプリの中（設定の一番下）に出す版（2026-10-14、本人「アプリ内でバージョンをわかるようにしてほしい」）
  define: {
    __APP_BUILT_AT__: JSON.stringify(new Date().toISOString()),
    __APP_COMMIT__: JSON.stringify((env.GITHUB_SHA ?? '').slice(0, 7)),
  },
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: false, // 登録は main.tsx の registerSW で行う
      includeAssets: ['seed/*.csv'],
      manifest: {
        name: 'pocamaster',
        short_name: 'pocamaster',
        description: 'IVE フォトカード収集管理',
        lang: 'ja',
        display: 'standalone',
        background_color: '#f5f0ed',
        theme_color: '#f5f0ed',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2,csv}'],
        // 手元の確認ページ（public/_review、Git に入れない）はアプリに含めない
        globIgnores: ['**/_review/**'],
      },
    }),
  ],
})
