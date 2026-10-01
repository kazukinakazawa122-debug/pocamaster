import { lazy, Suspense, useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import TabBar from './components/TabBar'
import { UndoProvider } from './components/Undo'
import ErrorBoundary from './components/ErrorBoundary'
import Home from './pages/Home'
import Collections from './pages/Collections'
import CollectionDetail from './pages/CollectionDetail'
import { MiniveLoading } from './components/Minive'

// 毎回は使わない画面は、開いたときに読み込む（最初の読み込みを軽くする。設定には ZIP を扱う大きな部品が入っている）
const CollectionEdit = lazy(() => import('./pages/CollectionEdit'))
const CardEdit = lazy(() => import('./pages/CardEdit'))
const BulkCreate = lazy(() => import('./pages/BulkCreate'))
const MyAlbums = lazy(() => import('./pages/MyAlbums'))
const Settings = lazy(() => import('./pages/Settings'))
// サイドバー（右上の 3 本線）から行く画面
const Search = lazy(() => import('./pages/Search'))
const Wants = lazy(() => import('./pages/Wants'))
const History = lazy(() => import('./pages/History'))

/**
 * iPhone で文字を入力するとキーボードが出て、画面（見えている範囲）がずれる。
 * そのままだと上のバーが画面の外へ行き、下のタブがキーボードの上に浮いてくるので、
 * 見えている範囲の上端に上のバーを合わせ、キーボードが出ている間は下のタブを隠す
 */
function useKeyboardFix() {
  useEffect(() => {
    const vv = window.visualViewport
    if (!vv) return
    const root = document.documentElement
    const update = () => {
      const keyboard = window.innerHeight - vv.height > 120
      root.classList.toggle('kb-open', keyboard)
      // 上のバーを動かすのはキーボードが出ているときだけ。一番下でさらに引っぱったとき（はね返り）にも
      // 見えている範囲がずれるので、いつも動かすとバーが下がってしまう（本人の報告、2026-09-30）
      root.style.setProperty('--vv-top', keyboard ? `${Math.max(0, vv.offsetTop)}px` : '0px')
    }
    update()
    vv.addEventListener('resize', update)
    vv.addEventListener('scroll', update)
    return () => {
      vv.removeEventListener('resize', update)
      vv.removeEventListener('scroll', update)
    }
  }, [])
}

export default function App() {
  const { pathname } = useLocation()
  useKeyboardFix()
  return (
    <UndoProvider>
      <div className="app">
        {/* 画面を移ったらエラー表示を消す */}
        <ErrorBoundary key={pathname}>
          <Suspense fallback={<MiniveLoading />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/collections" element={<Collections />} />
            <Route path="/collections/new" element={<CollectionEdit />} />
            <Route path="/collections/:id" element={<CollectionDetail />} />
            <Route path="/collections/:id/edit" element={<CollectionEdit />} />
            <Route path="/collections/:id/bulk" element={<BulkCreate />} />
            <Route path="/collections/:id/cards/new" element={<CardEdit />} />
            <Route path="/cards/:cardId/edit" element={<CardEdit />} />
            <Route path="/albums" element={<MyAlbums />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/search" element={<Search />} />
            <Route path="/wants" element={<Wants />} />
            <Route path="/history" element={<History />} />
          </Routes>
          </Suspense>
        </ErrorBoundary>
        <TabBar pathname={pathname} />
      </div>
    </UndoProvider>
  )
}
