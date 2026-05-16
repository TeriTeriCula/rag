import { useEffect, useRef, useState } from 'react'
import {
  uploadDocument,
  listDocuments,
  deleteDocument,
  getDocumentStatus,
  type DocumentRecord,
} from '../api/client'

const ALLOWED = ['.pdf', '.txt', '.docx']

function ext(name: string) {
  return '.' + name.split('.').pop()!.toLowerCase()
}

function StatusBadge({ record }: { record: DocumentRecord }) {
  const base = 'text-xs font-medium px-2 py-0.5 rounded-full'
  if (record.status === 'ready')
    return <span className={`${base} bg-green-100 text-green-700`}>Ready</span>
  if (record.status === 'processing')
    return <span className={`${base} bg-yellow-100 text-yellow-700`}>Processing…</span>
  return (
    <span title={record.error ?? ''} className={`${base} bg-red-100 text-red-700 cursor-help`}>
      Failed
    </span>
  )
}

export function DocumentPanel() {
  const [docs, setDocs] = useState<DocumentRecord[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchDocs = async () => {
    try {
      setDocs(await listDocuments())
    } catch {}
  }

  useEffect(() => {
    fetchDocs()
  }, [])

  useEffect(() => {
    const processing = docs.filter((d) => d.status === 'processing')
    if (processing.length && !pollRef.current) {
      pollRef.current = setInterval(async () => {
        const updates = await Promise.all(
          processing.map((d) => getDocumentStatus(d.doc_id).catch(() => d)),
        )
        setDocs((prev) => {
          const map = new Map(prev.map((d) => [d.doc_id, d]))
          for (const u of updates) map.set(u.doc_id, u as DocumentRecord)
          return Array.from(map.values())
        })
        if (updates.every((u) => (u as DocumentRecord).status !== 'processing')) {
          clearInterval(pollRef.current!)
          pollRef.current = null
        }
      }, 3000)
    }
    return () => {
      if (!processing.length && pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [docs])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadError(null)

    if (!ALLOWED.includes(ext(file.name))) {
      setUploadError(`Unsupported file type. Allowed: ${ALLOWED.join(', ')}`)
      e.target.value = ''
      return
    }

    setUploading(true)
    setUploadProgress(true)
    try {
      const result = await uploadDocument(file)
      setDocs((prev) => [
        ...prev,
        {
          doc_id: result.doc_id,
          filename: file.name,
          status: 'processing',
          uploaded_at: new Date().toISOString(),
        },
      ])
    } catch (err) {
      setUploadError((err as Error).message)
    } finally {
      setUploading(false)
      setUploadProgress(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId)
      setDocs((prev) => prev.filter((d) => d.doc_id !== docId))
    } catch (err) {
      alert((err as Error).message)
    } finally {
      setDeleteConfirm(null)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 border-l border-gray-200">
      <div className="px-4 py-3 border-b border-gray-200 bg-white">
        <h2 className="text-sm font-semibold text-gray-700">Documents</h2>
      </div>

      <div className="px-4 py-3 border-b border-gray-200 bg-white space-y-2">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt,.docx"
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          onClick={() => fileRef.current?.click()}
          disabled={uploading}
          className="w-full text-sm bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
        >
          {uploadProgress ? 'Uploading…' : '+ Upload Document'}
        </button>
        {uploadError && <p className="text-xs text-red-600">{uploadError}</p>}
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
        {docs.length === 0 && (
          <p className="text-xs text-gray-400 text-center mt-6">No documents yet.</p>
        )}
        {docs.map((doc) => (
          <div
            key={doc.doc_id}
            className="flex items-center gap-2 bg-white rounded-lg border border-gray-200 px-3 py-2 text-xs"
          >
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-800 truncate">{doc.filename}</p>
              <p className="text-gray-400">
                {new Date(doc.uploaded_at).toLocaleDateString()}
              </p>
            </div>
            <StatusBadge record={doc} />
            {deleteConfirm === doc.doc_id ? (
              <div className="flex gap-1">
                <button
                  onClick={() => handleDelete(doc.doc_id)}
                  className="text-red-600 hover:text-red-800 font-medium"
                >
                  Yes
                </button>
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  No
                </button>
              </div>
            ) : (
              <button
                onClick={() => setDeleteConfirm(doc.doc_id)}
                className="text-gray-300 hover:text-red-500 transition-colors ml-1"
                title="Delete"
              >
                ✕
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
