import { useEffect, useRef } from 'react'
import { CitationList } from './CitationList'
import type { Source } from '../api/client'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  streaming?: boolean
}

interface Props {
  messages: Message[]
}

export function ChatThread({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, messages[messages.length - 1]?.content])

  if (!messages.length) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
        Ask a question about your documents to get started.
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-sm'
                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
            }`}
          >
            {msg.streaming && !msg.content ? (
              <span className="flex gap-1 items-center h-4">
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
              </span>
            ) : (
              <p className="whitespace-pre-wrap">{msg.content}</p>
            )}
            {msg.sources && <CitationList sources={msg.sources} />}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
