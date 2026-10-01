import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { IconCards, IconSettings } from '@tabler/icons-react'
import { AlbumIcon, IveLogoIcon } from './TabIcons'

const TABS = [
  { to: '/', label: 'ホーム', Icon: IveLogoIcon, end: true },
  { to: '/collections', label: 'コレクション', Icon: IconCards, end: false },
  { to: '/albums', label: 'マイアルバム', Icon: AlbumIcon, end: false },
  { to: '/settings', label: '設定', Icon: IconSettings, end: false },
]

/** サイドバーから行く画面（下のタブのどれでもない） */
const MENU_PAGES = ['/search', '/wants', '/history']

/** いま開いているタブの番号（詳しい画面ではその親のタブ）。サイドバーの画面では -1（どのタブも選ばない） */
function tabIndex(pathname: string): number {
  if (MENU_PAGES.some((p) => pathname.startsWith(p))) return -1
  for (let i = TABS.length - 1; i > 0; i--) if (pathname.startsWith(TABS[i].to)) return i
  return 0
}

/** バーの内側の余白（.tabbar の padding と同じ） */
const INSET = 6
/** 押している間の丸の大きさ（浮き上がる） */
const LIFT = 1.16

const reduceMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false

/**
 * 下のタブ（本人の要望、2026-10-01：Instagram の「液体ガラス」のような丸）。
 * 押すと丸が少し大きくなって浮き、指の位置へ寄る。押したまま動かすと指についてきて、速く動かすと進む向きに伸びる。
 * 離すと一番近いタブへ、少し行き過ぎてから収まり、そのあと画面を切り替える。
 * 指についていく間は毎コマ位置を書き換え、離したあとの動きは Web Animations に任せる
 * （画面の切り替えで描く処理が重くても、丸の動きが止まらないように）
 */
export default function TabBar({ pathname }: { pathname: string }) {
  const navigate = useNavigate()
  const barRef = useRef<HTMLElement>(null)
  const pillRef = useRef<HTMLSpanElement>(null)
  const current = tabIndex(pathname)
  // 丸がいま指しているタブ（文字を濃くする）。押している間は指の下のタブ
  const [lit, setLit] = useState<number | null>(null)
  const press = useRef<{ id: number; x: number; t: number; v: number; moved: boolean } | null>(null)
  const [pressing, setPressing] = useState(false)
  /** 丸が向かっている（収まった）タブ。同じタブへの動きをやり直さないため */
  const target = useRef<number | null>(null)
  const anim = useRef<Animation | null>(null)
  const relax = useRef<number | undefined>(undefined)

  /** 1 つのタブの幅（丸の幅） */
  const slot = () => (barRef.current!.clientWidth - INSET * 2) / TABS.length
  /** 指の位置 → 丸の左端の位置（バーの中に収める） */
  const xFor = (clientX: number) => {
    const r = barRef.current!.getBoundingClientRect()
    return Math.min(slot() * (TABS.length - 1), Math.max(0, clientX - r.left - INSET - slot() / 2))
  }
  const indexAt = (clientX: number) => {
    const r = barRef.current!.getBoundingClientRect()
    return Math.min(TABS.length - 1, Math.max(0, Math.floor(((clientX - r.left - INSET) / (r.width - INSET * 2)) * TABS.length)))
  }
  /** いまの丸の位置と大きさ（動いている途中でも、見えているままの値） */
  const now = () => {
    const m = new DOMMatrix(getComputedStyle(pillRef.current!).transform)
    return { x: m.m41, sx: m.a, sy: m.d }
  }
  const tf = (x: number, sx: number, sy: number) => `translateX(${x}px) scale(${sx}, ${sy})`
  const setNow = (x: number, sx: number, sy: number) => {
    anim.current?.cancel()
    anim.current = null
    pillRef.current!.style.transform = tf(x, sx, sy)
  }
  /** 丸をタブ i に収める。dir は進んできた向き（少し行き過ぎてから戻る） */
  const settle = (i: number, fast = false) => {
    target.current = i
    const pill = pillRef.current!
    const from = now()
    const to = i * slot()
    const dist = to - from.x
    const end = tf(to, 1, 1)
    anim.current?.cancel()
    pill.style.transform = end
    if (reduceMotion()) return
    const over = Math.max(-10, Math.min(10, dist * 0.08))
    // 遠くへ行くときは途中で横に伸び、着いたら少し行き過ぎて戻る（ぷにっと収まる）
    anim.current = pill.animate(
      [
        { transform: tf(from.x, from.sx, from.sy) },
        { transform: tf(from.x + dist * 0.55, Math.max(from.sx, 1) * (1 + Math.min(0.22, Math.abs(dist) / 900)), Math.max(from.sy, 1) * 0.94), offset: 0.4 },
        { transform: tf(to + over, 1.03, 0.98), offset: 0.72 },
        { transform: end },
      ],
      { duration: fast ? 300 : 460, easing: 'cubic-bezier(.25,.8,.3,1)' },
    )
  }

  // 戻るボタンなど、押さずに画面が変わったときも丸を動かす
  useLayoutEffect(() => {
    if (press.current || !barRef.current) return
    setLit(null)
    // タブを押して切り替えたときは、もう丸がそこへ向かっているので動かし直さない
    if (current < 0 || target.current === current) return
    settle(current, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current])
  // 最初と、画面の幅が変わったときは、動かさずにその位置へ
  useEffect(() => {
    const place = () => {
      if (press.current || current < 0 || !barRef.current) return
      target.current = current
      setNow(current * slot(), 1, 1)
    }
    place()
    window.addEventListener('resize', place)
    return () => window.removeEventListener('resize', place)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const go = (i: number) => {
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

  /** 指の速さで丸を伸ばす（速いほど横に伸びて縦に縮む）。止まったら少しずつ戻す */
  const follow = (x: number) => {
    const p = press.current!
    const stretch = reduceMotion() ? 0 : Math.min(0.28, Math.abs(p.v) * 0.12)
    setNow(x, LIFT * (1 + stretch), LIFT * (1 - stretch * 0.45))
    window.clearTimeout(relax.current)
    relax.current = window.setTimeout(() => {
      if (!press.current) return
      press.current.v = 0
      const pill = pillRef.current!
      const from = now()
      anim.current = pill.animate([{ transform: tf(from.x, from.sx, from.sy) }, { transform: tf(from.x, LIFT, LIFT) }], {
        duration: 220,
        easing: 'cubic-bezier(.3,1.4,.5,1)',
        fill: 'forwards',
      })
    }, 60)
  }

  const shown = lit ?? current
  return (
    <nav
      ref={barRef}
      className={`tabbar${pressing ? ' pressing' : ''}${current < 0 && lit === null ? ' no-pill' : ''}`}
      onPointerDown={(e) => {
        if (e.button !== 0) return
        barRef.current!.setPointerCapture(e.pointerId)
        press.current = { id: e.pointerId, x: e.clientX, t: performance.now(), v: 0, moved: false }
        target.current = null
        setPressing(true)
        setLit(indexAt(e.clientX))
        // 浮き上がりながら指の位置へ寄る
        const pill = pillRef.current!
        const from = now()
        const to = xFor(e.clientX)
        anim.current?.cancel()
        pill.style.transform = tf(to, LIFT, LIFT)
        if (!reduceMotion()) {
          anim.current = pill.animate([{ transform: tf(from.x, from.sx, from.sy) }, { transform: tf(to, LIFT, LIFT) }], {
            duration: 200,
            easing: 'cubic-bezier(.3,1.3,.5,1)',
          })
        }
      }}
      onPointerMove={(e) => {
        const p = press.current
        if (!p || p.id !== e.pointerId) return
        const t = performance.now()
        const dx = e.clientX - p.x
        if (!p.moved && Math.abs(dx) < 3) return
        p.moved = true
        // 速さ（px/ms）。急に変わらないよう前の値と混ぜる
        p.v = p.v * 0.5 + (dx / Math.max(1, t - p.t)) * 0.5
        p.x = e.clientX
        p.t = t
        follow(xFor(e.clientX))
        const i = indexAt(e.clientX)
        if (i !== lit) setLit(i)
      }}
      onPointerUp={(e) => {
        const p = press.current
        if (!p || p.id !== e.pointerId) return
        press.current = null
        setPressing(false)
        window.clearTimeout(relax.current)
        const i = indexAt(e.clientX)
        settle(i)
        if (TABS[i].to === pathname) {
          // いま開いている画面のタブをもう一度押したら、一番上までスクロールする
          setLit(null)
          if (!p.moved) window.scrollTo({ top: 0, behavior: 'smooth' })
        } else {
          setLit(i)
          go(i)
        }
      }}
      onPointerCancel={() => {
        press.current = null
        setPressing(false)
        window.clearTimeout(relax.current)
        setLit(null)
        if (current >= 0) settle(current, true)
      }}
    >
      <span ref={pillRef} className="tab-pill" aria-hidden />
      {TABS.map(({ to, label, Icon, end }, i) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={() => (i === shown ? 'active' : '')}
          onClick={(e) => {
            e.preventDefault()
            // 指・マウスで押したときは onPointerUp で切り替え済み。キーボード（Enter）のときだけここで切り替える
            if (e.detail !== 0) return
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
