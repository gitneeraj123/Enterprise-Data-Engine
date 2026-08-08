import { Link, useNavigate } from 'react-router-dom'
import ChatWindow from '../components/ChatWindow'

export default function Chat() {
  const navigate = useNavigate()
  const isAdmin = localStorage.getItem('role') === 'admin'
  function logout() { localStorage.clear(); navigate('/login') }
  return <main><nav><strong>Enterprise Data Engine</strong><span>{isAdmin && <Link to="/admin">Admin dashboard</Link>}<button onClick={logout}>Log out</button></span></nav><ChatWindow /></main>
}
