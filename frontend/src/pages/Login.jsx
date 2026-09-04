import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { loading, signIn, user } = useAuth()

  if (loading) return <main className="auth">Checking session…</main>
  if (user) return <Navigate to="/chat" replace />

  async function submit(event) {
    event.preventDefault()
    setError('')
    try {
      await signIn(username, password)
      navigate('/chat')
    } catch (err) { setError(err.message) }
  }

  return <main className="auth"><form onSubmit={submit}><h1>Enterprise Data Engine</h1>
    <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} required /></label>
    <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
    {error && <p className="error">{error}</p>}<button>Sign in</button>
  </form></main>
}
