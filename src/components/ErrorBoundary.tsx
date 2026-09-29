import { Component, type ReactNode } from 'react'

interface State {
  error: Error | null
}

/** 画面の表示でエラーが起きたとき、白い画面にせず、内容と「読み込み直す」ボタンを出す */
export default class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="page empty">
        <p>表示中にエラーが起きました</p>
        <p className="xs muted" style={{ wordBreak: 'break-all' }}>
          {this.state.error.message}
        </p>
        <button className="btn primary" onClick={() => location.reload()}>
          読み込み直す
        </button>
      </div>
    )
  }
}
