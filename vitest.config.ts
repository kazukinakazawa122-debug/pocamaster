import { defineConfig } from 'vitest/config'

// 自動テスト（npm test）。ブラウザの IndexedDB は fake-indexeddb で代用する（2026-10-03）
export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['fake-indexeddb/auto'],
    include: ['src/**/*.test.ts'],
  },
})
