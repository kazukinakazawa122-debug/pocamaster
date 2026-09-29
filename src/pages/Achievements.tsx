import { TrophyIcon } from '../components/TabIcons'
import { TopBar } from '../components/ui'

/** S-08 実績（第 2 段階で作る） */
export default function Achievements() {
  return (
    <div className="page">
      <TopBar title="実績" />
      <div className="empty">
        <TrophyIcon size={48} stroke={1.2} aria-hidden />
        <p>バッジと収集グラフは次の段階で追加します</p>
        <p className="small">集めた記録は今から保存されています。</p>
      </div>
    </div>
  )
}
