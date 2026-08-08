import { useState } from 'react'
import { registerUser } from '../api/client'

export default function CreateUserModal({ onClose }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setCreating(true)
    setError('')
    try {
      await registerUser(username.trim(), password, 'employee')
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <form className="modal" onSubmit={submit}>
        <h2>Create employee account</h2>
        <p className="muted">Employee accounts can chat but cannot manage documents or users.</p>
        <label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} required /></label>
        <label>Password<input type="password" minLength="8" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        {error && <p className="error">{error}</p>}
        <div><button type="button" onClick={onClose}>Cancel</button><button disabled={creating}>{creating ? 'Creating…' : 'Create account'}</button></div>
      </form>
    </div>
  )
}
