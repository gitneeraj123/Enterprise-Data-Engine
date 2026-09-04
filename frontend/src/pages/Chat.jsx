import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import ChatWindow from '../components/ChatWindow'

export default function Chat() {
  const navigate = useNavigate()
  const { signOut, user } = useAuth()
  const [loggingOut, setLoggingOut] = useState(false)
  const [logoutError, setLogoutError] = useState('')
  const isAdmin = user?.role === 'admin'

  async function handleLogout() {
    setLogoutError('')
    setLoggingOut(true)
    try {
      await signOut()
      navigate('/login')
    } catch (err) {
      setLogoutError(err.message)
    } finally {
      setLoggingOut(false)
    }
  }

  return <main><nav><strong>Enterprise Data Engine</strong><span>{isAdmin && <Link to="/admin">Admin dashboard</Link>}<button onClick={handleLogout} disabled={loggingOut}>{loggingOut ? 'Logging out…' : 'Log out'}</button></span></nav>{logoutError && <p className="error">{logoutError}</p>}<ChatWindow /></main>
}
