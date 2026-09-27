import { NavLink, Route, Routes } from 'react-router-dom'
import { IconBooks, IconHome, IconSettings, IconTrophy } from '@tabler/icons-react'
import { UndoProvider } from './components/Undo'
import Home from './pages/Home'
import Collections from './pages/Collections'
import CollectionDetail from './pages/CollectionDetail'
import CollectionEdit from './pages/CollectionEdit'
import CardEdit from './pages/CardEdit'
import BulkCreate from './pages/BulkCreate'
import Achievements from './pages/Achievements'
import Settings from './pages/Settings'

const TABS = [
  { to: '/', label: 'ホーム', Icon: IconHome, end: true },
  { to: '/collections', label: 'コレクション', Icon: IconBooks, end: false },
  { to: '/achievements', label: '実績', Icon: IconTrophy, end: false },
  { to: '/settings', label: '設定', Icon: IconSettings, end: false },
]

export default function App() {
  return (
    <UndoProvider>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/collections" element={<Collections />} />
          <Route path="/collections/new" element={<CollectionEdit />} />
          <Route path="/collections/:id" element={<CollectionDetail />} />
          <Route path="/collections/:id/edit" element={<CollectionEdit />} />
          <Route path="/collections/:id/bulk" element={<BulkCreate />} />
          <Route path="/collections/:id/cards/new" element={<CardEdit />} />
          <Route path="/cards/:cardId/edit" element={<CardEdit />} />
          <Route path="/achievements" element={<Achievements />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
        <nav className="tabbar">
          {TABS.map(({ to, label, Icon, end }) => (
            <NavLink key={to} to={to} end={end}>
              <Icon size={24} stroke={1.6} aria-hidden />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </UndoProvider>
  )
}
