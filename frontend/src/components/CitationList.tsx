import { useState } from 'react'
import type { Source } from '../api/client'

interface Props {
  sources: Source[]
}

export function CitationList({ sources }: Props) {
  const [open, setOpen] = useState<number | null>(null)

  if (!sources.length) return null

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {sources.map((s, i) => (
        <div key={i} className="relative">
          <button
            onClick={() => setOpen(open === i ? null : i)}
            className="text-xs bg-blue-50 border border-blue-200 text-blue-700 rounded-full px-3 py-1 hover:bg-blue-100 transition-colors"
          >
            {s.filename} #{s.chunk_index}
          </button>
          {open === i && (
            <div className="absolute z-10 bottom-full mb-1 left-0 w-72 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-xs text-gray-700">
              <p className="font-semibold mb-1">{s.filename}</p>
              <p className="line-clamp-5">{s.excerpt}</p>
              <p className="mt-1 text-gray-400">similarity: {s.similarity}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
