import { useState } from 'react'
import { uploadDocument } from '../api/client'

export default function UploadModal({ onClose, onUploaded }) {
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    if (!file) return setError('Choose a PDF file.')
    setUploading(true); setError('')
    try {
      const document = await uploadDocument(file)
      onUploaded(document)
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <form className="modal" onSubmit={submit}>
        <h2>Upload document</h2>
        <input type="file" accept="application/pdf,.pdf" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        {error && <p className="error">{error}</p>}
        <div><button type="button" onClick={onClose}>Cancel</button><button disabled={uploading}>{uploading ? 'Uploading…' : 'Upload PDF'}</button></div>
      </form>
    </div>
  )
}
