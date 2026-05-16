import { useRef, useState } from 'react'

interface Props {
  onSubmit: (query: string) => void
  disabled: boolean
}

export function ChatInput({ onSubmit, disabled }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const q = value.trim()
    if (!q || disabled) return
    onSubmit(q)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3">
      <div className="flex gap-2 items-end max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={value}
          disabled={disabled}
          rows={1}
          placeholder="Ask a question about your documents…"
          className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed overflow-hidden"
          style={{ maxHeight: '8rem' }}
          onChange={(e) => {
            setValue(e.target.value)
            e.target.style.height = 'auto'
            e.target.style.height = `${e.target.scrollHeight}px`
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit()
            }
          }}
        />
        <button
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="shrink-0 bg-blue-600 text-white rounded-xl px-4 py-2.5 text-sm font-medium hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}
