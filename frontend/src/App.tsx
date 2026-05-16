import { useState, useCallback } from 'react'
import { ChatThread, type Message } from './components/ChatThread'
import { ChatInput } from './components/ChatInput'
import { DocumentPanel } from './components/DocumentPanel'
import { streamQuery } from './hooks/useSSEQuery'
import type { HistoryTurn } from './api/client'
import './index.css'

let msgCounter = 0
const uid = () => String(++msgCounter)

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [history, setHistory] = useState<HistoryTurn[]>([])
  const [generating, setGenerating] = useState(false)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const handleQuery = useCallback(
    async (query: string) => {
      if (generating) return
      setGenerating(true)

      const userMsg: Message = { id: uid(), role: 'user', content: query }
      const assistantId = uid()
      const assistantMsg: Message = {
        id: assistantId,
        role: 'assistant',
        content: '',
        streaming: true,
        sources: [],
      }

      setMessages((prev) => [...prev, userMsg, assistantMsg])

      let answer = ''

      await streamQuery(query, history, {
        onSources: (s) => {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, sources: s } : m)),
          )
        },
        onToken: (token) => {
          answer += token
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, content: answer } : m)),
          )
        },
        onDone: () => {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, streaming: false } : m)),
          )
          setHistory((prev) => [
            ...prev,
            { role: 'user', content: query },
            { role: 'assistant', content: answer },
          ])
          setGenerating(false)
        },
        onError: (err) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: `Error: ${err.message}`, streaming: false }
                : m,
            ),
          )
          setGenerating(false)
        },
      })
    },
    [generating, history],
  )

  return (
    <div className="flex h-dvh overflow-hidden">
      {/* Mobile drawer overlay */}
      {drawerOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-20 lg:hidden"
          onClick={() => setDrawerOpen(false)}
        />
      )}

      {/* Main chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        <header className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 bg-white shrink-0">
          <button
            className="lg:hidden text-gray-500 hover:text-gray-800 text-xl leading-none"
            onClick={() => setDrawerOpen(true)}
          >
            ☰
          </button>
          <h1 className="text-base font-semibold text-gray-800">RAG Assistant</h1>
        </header>

        <ChatThread messages={messages} />
        <ChatInput onSubmit={handleQuery} disabled={generating} />
      </div>

      {/* Sidebar — always visible on desktop, drawer on tablet/mobile */}
      <aside
        className={`
          fixed top-0 right-0 h-full w-72 z-30 transition-transform duration-300
          lg:static lg:translate-x-0 lg:w-72 lg:shrink-0
          ${drawerOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
        `}
      >
        <DocumentPanel />
      </aside>
    </div>
  )
}
