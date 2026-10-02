import { Component, type ReactNode } from 'react'

interface State {
  error: Error | null
}

/**
 * 画面の表示でエラーが起きたとき、白い画面にせず、内容と「読み込み直す」ボタンを出す。
 * resetKey（いまの画面の場所）が変わったら、エラーの表示を消す。
 * 前は画面を移るたびに key で作り直していたが、そうすると中の Suspense も作り直され、
 * React が表示を 0.3 秒ためてから出すため、どの画面へ移っても 0.3 秒待っていた（2026-10-02）
 */
export default class ErrorBoundary extends Component<{ children: ReactNode; resetKey?: string }, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidUpdate(prev: { resetKey?: string }) {
    if (this.state.error && prev.resetKey !== this.props.resetKey) this.setState({ error: null })
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
