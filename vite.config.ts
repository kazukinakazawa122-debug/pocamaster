import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// GitHub Pages ではリポジトリ名のパス（/pocamaster/）の下に置かれる
export default defineConfig({
  base: '/pocamaster/',
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
