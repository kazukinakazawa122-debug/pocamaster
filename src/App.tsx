import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { NavLink, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { IconCards, IconSettings } from '@tabler/icons-react'
import { AlbumIcon, IveLogoIcon } from './components/TabIcons'
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

const TABS = [
  { to: '/', label: 'ホーム', Icon: IveLogoIcon, end: true },
  { to: '/collections', label: 'コレクション', Icon: IconCards, end: false },
  { to: '/albums', label: 'マイアルバム', Icon: AlbumIcon, end: false },
  { to: '/settings', label: '設定', Icon: IconSettings, end: false },
]

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
          </Routes>
          </Suspense>
        </ErrorBoundary>
        <TabBar pathname={pathname} />
      </div>
    </UndoProvider>
  )
}

/** いま開いているタブの番号（詳しい画面ではその親のタブ） */
function tabIndex(pathname: string): number {
  for (let i = TABS.length - 1; i > 0; i--) if (pathname.startsWith(TABS[i].to)) return i
  return 0
}

/**
 * 下のタブ（本人の要望、2026-10-01：Instagram のような浮いた丸いバー）。
 * 選んでいるタブの後ろの丸が動く。バーの上で指を左右にすべらせると丸がついてきて、指を離したタブに移る
 */
function TabBar({ pathname }: { pathname: string }) {
  const navigate = useNavigate()
  const ref = useRef<HTMLElement>(null)
  const current = tabIndex(pathname)
  const [drag, setDrag] = useState<number | null>(null)
  const start = useRef<{ x: number; moved: boolean } | null>(null)
  const dragged = useRef(false)
  const indexAt = (clientX: number) => {
    const r = ref.current!.getBoundingClientRect()
    return Math.min(TABS.length - 1, Math.max(0, Math.floor(((clientX - r.left) / r.width) * TABS.length)))
  }
  const shown = drag ?? current
  return (
    <nav
      ref={ref}
      className={`tabbar${drag !== null ? ' dragging' : ''}`}
      onPointerDown={(e) => {
        start.current = { x: e.clientX, moved: false }
      }}
      onPointerMove={(e) => {
        if (!start.current) return
        if (!start.current.moved && Math.abs(e.clientX - start.current.x) < 8) return
        if (!start.current.moved) {
          start.current.moved = true
          // すべらせ始めてから指を追う（タップのときはリンクをそのまま押せるように、最初は追わない）
          ref.current?.setPointerCapture(e.pointerId)
        }
        setDrag(indexAt(e.clientX))
      }}
      onPointerUp={(e) => {
        const s = start.current
        start.current = null
        if (!s?.moved) return
        dragged.current = true
        window.setTimeout(() => (dragged.current = false), 50)
        const i = indexAt(e.clientX)
        setDrag(null)
        if (TABS[i].to !== pathname) navigate(TABS[i].to)
      }}
      onPointerCancel={() => {
        start.current = null
        setDrag(null)
      }}
      onClickCapture={(e) => {
        // すべらせて選んだときは、指を離した場所のリンクのクリックを使わない
        if (dragged.current) e.preventDefault()
      }}
    >
      <span className="tab-pill" style={{ transform: `translateX(${shown * 100}%)` }} aria-hidden />
      {TABS.map(({ to, label, Icon, end }, i) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={() => (i === shown ? 'active' : '')}
          onClick={(e) => {
            // いま開いている画面のタブをもう一度押したら、一番上までスクロールする
            if (pathname === to) {
              e.preventDefault()
              window.scrollTo({ top: 0, behavior: 'smooth' })
            }
          }}
        >
          <span className="tab-ic">
            <Icon size={24} stroke={1.6} aria-hidden />
          </span>
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
