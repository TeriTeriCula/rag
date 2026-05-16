import { createParser } from 'eventsource-parser'
import type { Source, HistoryTurn } from '../api/client'

export interface SSEQueryCallbacks {
  onSources: (sources: Source[]) => void
  onToken: (token: string) => void
  onDone: () => void
  onError: (err: Error) => void
}

export async function streamQuery(
  query: string,
  history: HistoryTurn[],
  callbacks: SSEQueryCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch('/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ query, history, top_k: 5 }),
    signal,
  })

  if (!res.ok || !res.body) {
    callbacks.onError(new Error(`Query failed: ${res.statusText}`))
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()

  const parser = createParser({
    onEvent(event) {
      if (event.event === 'sources') {
        try { callbacks.onSources(JSON.parse(event.data)) } catch {}
        return
      }
      if (event.data === '[DONE]') {
        callbacks.onDone()
        return
      }
      try {
        const parsed = JSON.parse(event.data)
        if (parsed.token) callbacks.onToken(parsed.token)
      } catch {}
    },
  })

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    parser.feed(decoder.decode(value, { stream: true }))
  }
}
