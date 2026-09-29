import { NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { IconCards, IconSettings } from '@tabler/icons-react'
import { AlbumIcon, IveLogoIcon } from './components/TabIcons'
import { UndoProvider } from './components/Undo'
import ErrorBoundary from './components/ErrorBoundary'
import Home from './pages/Home'
import Collections from './pages/Collections'
import CollectionDetail from './pages/CollectionDetail'
import CollectionEdit from './pages/CollectionEdit'
import CardEdit from './pages/CardEdit'
import BulkCreate from './pages/BulkCreate'
import MyAlbums from './pages/MyAlbums'
import Settings from './pages/Settings'

const TABS = [
  { to: '/', label: 'ホーム', Icon: IveLogoIcon, end: true },
  { to: '/collections', label: 'コレクション', Icon: IconCards, end: false },
  { to: '/albums', label: 'マイアルバム', Icon: AlbumIcon, end: false },
  { to: '/settings', label: '設定', Icon: IconSettings, end: false },
]

export default function App() {
  const { pathname } = useLocation()
  return (
    <UndoProvider>
      <div className="app">
        {/* 画面を移ったらエラー表示を消す */}
        <ErrorBoundary key={pathname}>
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
          </Routes>
        </ErrorBoundary>
        <nav className="tabbar">
          {TABS.map(({ to, label, Icon, end }) => (
            <NavLink key={to} to={to} end={end}>
              <span className="tab-ic">
                <Icon size={24} stroke={1.6} aria-hidden />
              </span>
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </UndoProvider>
  )
}
