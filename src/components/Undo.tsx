import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from 'react'

interface UndoItem {
  message: string
  undo: () => void
}

const UndoContext = createContext<(message: string, undo: () => void) => void>(() => {})

/** 切り替えたあとに「元に戻す」を 3 秒だけ出す */
export function UndoProvider({ children }: { children: ReactNode }) {
  const [item, setItem] = useState<UndoItem | null>(null)
  const timer = useRef<number | undefined>(undefined)

  const show = useCallback((message: string, undo: () => void) => {
    window.clearTimeout(timer.current)
    setItem({ message, undo })
    timer.current = window.setTimeout(() => setItem(null), 3000)
  }, [])

  return (
    <UndoContext.Provider value={show}>
      {children}
      {item && (
        <div className="toast" role="status">
          <span>{item.message}</span>
          <button
            onClick={() => {
              item.undo()
              window.clearTimeout(timer.current)
              setItem(null)
            }}
          >
            元に戻す
          </button>
        </div>
      )}
    </UndoContext.Provider>
  )
}

export function useUndo() {
  return useContext(UndoContext)
}
