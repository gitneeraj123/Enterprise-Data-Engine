import { useEffect, useState } from 'react'
import { deleteDocument, getDocuments } from '../api/client'
import CreateUserModal from '../components/CreateUserModal'
import DocumentTable from '../components/DocumentTable'
import UploadModal from '../components/UploadModal'

export default function AdminDashboard() {
  const [documents, setDocuments] = useState([])
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [showCreateUser, setShowCreateUser] = useState(false)
  useEffect(() => { getDocuments().then(setDocuments).catch((err) => setError(err.message)) }, [])
  async function remove(document) {
    if (!window.confirm(`Delete ${document.filename}?`)) return
    try { await deleteDocument(document.id); setDocuments((items) => items.filter((item) => item.id !== document.id)) }
    catch (err) { setError(err.message) }
  }
  return <main><nav><strong>Admin dashboard</strong><a href="/chat">Back to chat</a></nav><section className="dashboard"><div className="dashboard-actions"><button onClick={() => setShowUpload(true)}>Upload Document</button><button onClick={() => setShowCreateUser(true)}>Create Employee Account</button></div>{error && <p className="error">{error}</p>}<DocumentTable documents={documents} onDelete={remove} /></section>{showUpload && <UploadModal onClose={() => setShowUpload(false)} onUploaded={(document) => setDocuments((items) => [document, ...items])} />}{showCreateUser && <CreateUserModal onClose={() => setShowCreateUser(false)} />}</main>
}
