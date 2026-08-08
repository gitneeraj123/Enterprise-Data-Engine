import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setError('')
    try {
      const response = await login(username, password)
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('role', response.role)
      navigate('/chat')
    } catch (err) { setError(err.message) }
  }

  return <main className="auth"><form onSubmit={submit}><h1>Enterprise Data Engine</h1>
    <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} required /></label>
    <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>
    {error && <p className="error">{error}</p>}<button>Sign in</button>
  </form></main>
}
