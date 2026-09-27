import { MEMBERS, type MemberId } from '../lib/members'

/** メンバーを複数選ぶ（ユニットカード用） */
export default function MemberPicker({ value, onChange }: { value: MemberId[]; onChange: (v: MemberId[]) => void }) {
  const all = value.length === MEMBERS.length
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      <button type="button" className={`chip${all ? ' on' : ''}`} onClick={() => onChange(all ? [] : MEMBERS.map((m) => m.id))}>
        全員
      </button>
      {MEMBERS.map((m) => {
        const on = value.includes(m.id)
        return (
          <button
            key={m.id}
            type="button"
            className="chip"
            aria-pressed={on}
            style={on ? { background: m.color, borderColor: m.color, color: m.on } : { color: m.text }}
            onClick={() => onChange(on ? value.filter((v) => v !== m.id) : [...value, m.id])}
          >
            {m.name}
          </button>
        )
      })}
    </div>
  )
}
