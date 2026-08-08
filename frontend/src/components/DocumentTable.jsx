export default function DocumentTable({ documents, onDelete }) {
  if (!documents.length) return <p className="muted">No documents have been uploaded.</p>
  return (
    <table>
      <thead><tr><th>Filename</th><th>Uploaded by</th><th>Uploaded at</th><th>Status</th><th /></tr></thead>
      <tbody>
        {documents.map((document) => (
          <tr key={document.id}>
            <td>{document.filename}</td><td>{document.uploaded_by}</td>
            <td>{new Date(document.uploaded_at).toLocaleString()}</td><td>{document.status}</td>
            <td><button className="danger" onClick={() => onDelete(document)}>Delete</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
