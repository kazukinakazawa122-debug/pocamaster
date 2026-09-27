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
      includeAssets: ['icon.svg', 'seed/*.csv'],
      manifest: {
        name: 'pocamaster',
        short_name: 'pocamaster',
        description: 'IVE フォトカード収集管理',
        lang: 'ja',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#ffffff',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icon.svg', sizes: 'any', type: 'image/svg+xml' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2,csv}'],
      },
    }),
  ],
})
