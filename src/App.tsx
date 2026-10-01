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
// サイドバー（右上の 3 本線）から行く画面
const Search = lazy(() => import('./pages/Search'))
const Wants = lazy(() => import('./pages/Wants'))
const History = lazy(() => import('./pages/History'))

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

/** サイドバーから行く画面（下のタブのどれでもない） */
const MENU_PAGES = ['/search', '/wants', '/history']

/** いま開いているタブの番号（詳しい画面ではその親のタブ）。サイドバーの画面では -1（どのタブも選ばない） */
function tabIndex(pathname: string): number {
  if (MENU_PAGES.some((p) => pathname.startsWith(p))) return -1
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
  // 押したタブ。押した瞬間に丸を動かし始め、画面の切り替えはそのあとにする（本人の報告、2026-10-01「丸の動きが滑らかでない」）。
  // 画面を描く間は丸の動きが止まりやすいので、先に動かしておく
  const [pending, setPending] = useState<number | null>(null)
  useEffect(() => setPending(null), [pathname])
  const go = (i: number) => {
    setPending(i)
    // 丸が動き始めてから（2 コマ待ってから）画面を切り替える。コマが来ないとき（画面が隠れているなど）も少しで切り替える
    let done = false
    const run = () => {
      if (done) return
      done = true
      navigate(TABS[i].to)
    }
    requestAnimationFrame(() => requestAnimationFrame(run))
    window.setTimeout(run, 80)
  }
  const [drag, setDrag] = useState<number | null>(null)
  const start = useRef<{ x: number; moved: boolean } | null>(null)
  const dragged = useRef(false)
  const indexAt = (clientX: number) => {
    const r = ref.current!.getBoundingClientRect()
    return Math.min(TABS.length - 1, Math.max(0, Math.floor(((clientX - r.left) / r.width) * TABS.length)))
  }
  const shown = drag ?? pending ?? current
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
        if (TABS[i].to !== pathname) go(i)
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
      <span className="tab-pill" style={{ transform: `translateX(${Math.max(0, shown) * 100}%)`, opacity: shown < 0 ? 0 : undefined }} aria-hidden />
      {TABS.map(({ to, label, Icon, end }, i) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={() => (i === shown ? 'active' : '')}
          onClick={(e) => {
            if (e.defaultPrevented) return
            e.preventDefault()
            // いま開いている画面のタブをもう一度押したら、一番上までスクロールする
            if (pathname === to) window.scrollTo({ top: 0, behavior: 'smooth' })
            else go(i)
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
