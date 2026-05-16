export interface DocumentRecord {
  doc_id: string
  filename: string
  status: 'processing' | 'ready' | 'failed'
  uploaded_at: string
  error?: string | null
  source_url?: string | null
}

export interface Source {
  filename: string
  chunk_index: number
  excerpt: string
  similarity: number
}

export interface HistoryTurn {
  role: 'user' | 'assistant'
  content: string
}

export async function uploadDocument(file: File): Promise<{ doc_id: string; status: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/documents', { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Upload failed')
  }
  return res.json()
}

export async function listDocuments(): Promise<DocumentRecord[]> {
  const res = await fetch('/documents')
  if (!res.ok) throw new Error('Failed to fetch documents')
  return res.json()
}

export async function getDocumentStatus(docId: string): Promise<DocumentRecord> {
  const res = await fetch(`/documents/${docId}/status`)
  if (!res.ok) throw new Error('Failed to fetch status')
  return res.json()
}

export async function scrapeUrl(url: string): Promise<{ doc_id: string; status: string; source_url: string }> {
  const res = await fetch('/documents/url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Scrape failed')
  }
  return res.json()
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`/documents/${docId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Delete failed')
}

export interface QueryResult {
  answer: string
  sources: Source[]
}

export async function queryRag(
  query: string,
  history: HistoryTurn[],
  topK = 5,
): Promise<QueryResult> {
  const res = await fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, history, top_k: topK }),
  })
  if (!res.ok) throw new Error('Query failed')
  return res.json()
}
