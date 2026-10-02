import { useDeferredValue, useMemo, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { useSearchParams } from 'react-router-dom'
import { IconSearch, IconX } from '@tabler/icons-react'
import { db, type Card, type Collection } from '../lib/db'
import { useAllCards } from '../lib/cardStore'
import { MEMBER_BY_ID, MEMBERS, type MemberId } from '../lib/members'
import { TopBar } from '../components/ui'
import CardGroups, { type CardGroup } from '../components/CardGroups'
import { MiniveLoading } from '../components/Minive'

const STATUS_FILTERS = ['すべて', '未所持', '所持中'] as const
/** 何を入れればいいか迷わないよう、押すと入る言葉の例 */
const EXAMPLES = ['withmuu', 'Soundwave', 'ポラ', 'ラキドロ', 'ファンサイン', 'Tower Records', 'シーグリ']

/** 全角・半角、大文字・小文字、カタカナ・ひらがなの違いを無視して比べる */
function fold(s: string): string {
  return s
    .normalize('NFKC')
    .toLowerCase()
    .replace(/[ァ-ヶ]/g, (ch) => String.fromCharCode(ch.charCodeAt(0) - 0x60))
}

// 同じ意味の言葉（「ポラ」で POLA も見つける）
const ALIASES: Record<string, string> = { ぽら: 'pola', pola: 'ぽら', しーぐり: 'しーずんぐりーてぃんぐ', ふぁんさいん: 'fansign', fansign: 'ふぁんさいん' }

function haystack(c: Card, col: Collection): string {
  const members = c.memberIds.map((id) => `${MEMBER_BY_ID[id].name} ${id}`).join(' ')
  const all = c.memberIds.length === MEMBERS.length ? ' 全員' : ''
  return fold([col.name, col.type, col.releaseDate.slice(0, 4), c.source, c.version, members + all].join(' '))
}

/** 言葉をすべて含むカードを探す（空白で区切ると「かつ」になる） */
function matches(text: string, words: string[]): boolean {
  return words.every((w) => text.includes(w) || (ALIASES[w] !== undefined && text.includes(ALIASES[w])))
}

/** カードを探す（本人の要望、2026-10-01）：店の名前・バージョン・コレクション名などで、全部のカードから探す */
export default function Search() {
  const [params, setParams] = useSearchParams()
  // 打っている文字はこの画面で持つ（アドレスの書き換えを待つと、日本語の入力中に文字が飛ぶことがあるため）。
  // アドレスにも入れておき、カードを開いて「戻る」で来たときに同じ結果を出す
  const [q, setQ] = useState(() => params.get('q') ?? '')
  const member = (params.get('m') as MemberId | null) ?? null
  const status = (params.get('s') as (typeof STATUS_FILTERS)[number] | null) ?? 'すべて'
  const setParam = (key: string, value: string | null) => {
    const next = new URLSearchParams(params)
    if (value === null || value === '') next.delete(key)
    else next.set(key, value)
    setParams(next, { replace: true })
  }

  // カードは手元の記録から（開くたびに 6,000 枚を読み直さない）
  const collections = useLiveQuery(() => db.collections.toArray())
  const cards = useAllCards()
  const data = useMemo(() => (collections && cards ? { collections, cards } : undefined), [collections, cards])
  // 調べる文字（ひとつずつ作ると重いので、データが変わったときだけ作る）
  const index = useMemo(() => {
    if (!data) return null
    const colById = new Map(data.collections.map((c) => [c.id, c]))
    return data.cards.flatMap((c) => {
      const col = colById.get(c.collectionId)
      return col ? [{ c, col, text: haystack(c, col) }] : []
    })
  }, [data])

  // 打っている間は前の結果を出しておき、手が止まったら探す（1 文字ごとに待たせない）
  const query = useDeferredValue(q)
  const words = fold(query).split(/\s+/).filter(Boolean)
  const groups = useMemo(() => {
    if (!index || words.length === 0) return []
    const byCol = new Map<string, CardGroup>()
    for (const x of index) {
      if (member && !x.c.memberIds.includes(member)) continue
      if (status !== 'すべて' && x.c.status !== status) continue
      if (!matches(x.text, words)) continue
      let g = byCol.get(x.col.id)
      if (!g) byCol.set(x.col.id, (g = { col: x.col, cards: [] }))
      g.cards.push(x.c)
    }
    const list = [...byCol.values()]
    list.forEach((g) => g.cards.sort((a, b) => a.order - b.order))
    // 新しいコレクションを上に
    return list.sort((a, b) => b.col.releaseDate.localeCompare(a.col.releaseDate))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [index, words.join(' '), member, status])
  const count = groups.reduce((n, g) => n + g.cards.length, 0)

  return (
    <div className="page">
      <TopBar title="カードを探す" back menu />
      <div className="search-box">
        <IconSearch size={18} className="muted" aria-hidden />
        <input
          type="search"
          inputMode="search"
          enterKeyHint="search"
          placeholder="店の名前・バージョン・アルバム名など"
          aria-label="探す言葉"
          value={q}
          onChange={(e) => {
            setQ(e.target.value)
            setParam('q', e.target.value)
          }}
        />
        {q && (
          <button
            className="icon-btn"
            aria-label="消す"
            onClick={() => {
              setQ('')
              setParam('q', null)
            }}
            style={{ minWidth: 36, minHeight: 36 }}
          >
            <IconX size={18} />
          </button>
        )}
      </div>
      <div className="chips" style={{ margin: '10px 0 6px' }}>
        <button className={`chip${!member ? ' on' : ''}`} onClick={() => setParam('m', null)}>
          全員
        </button>
        {MEMBERS.map((m) => {
          const on = member === m.id
          return (
            <button
              key={m.id}
              className="chip"
              style={on ? { background: m.color, borderColor: m.color, color: m.on } : { color: m.text }}
              onClick={() => setParam('m', on ? null : m.id)}
            >
              {m.name}
            </button>
          )
        })}
      </div>
      <div className="chips" style={{ marginBottom: 4 }}>
        {STATUS_FILTERS.map((s) => (
          <button key={s} className={`chip${status === s ? ' on' : ''}`} onClick={() => setParam('s', s === 'すべて' ? null : s)}>
            {s}
          </button>
        ))}
      </div>

      {!data ? (
        <MiniveLoading />
      ) : words.length === 0 ? (
        <div style={{ marginTop: 20 }}>
          <div className="small muted" style={{ marginBottom: 8 }}>
            たとえば（空白で区切ると両方を含むカード）
          </div>
          <div className="chips" style={{ flexWrap: 'wrap' }}>
            {EXAMPLES.map((w) => (
              <button
                key={w}
                className="chip"
                onClick={() => {
                  setQ(w)
                  setParam('q', w)
                }}
              >
                {w}
              </button>
            ))}
          </div>
        </div>
      ) : count === 0 ? (
        <div className="empty">見つかりませんでした</div>
      ) : (
        <>
          <div className="small muted" style={{ marginTop: 10 }}>
            {groups.length} コレクション・{count} 枚
          </div>
          {/* 探す言葉が変わったら「もっと見る」を最初に戻す */}
          <CardGroups key={`${words.join(' ')}|${member}|${status}`} groups={groups} />
        </>
      )}
    </div>
  )
}
