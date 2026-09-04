import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function ProtectedRoute({ adminOnly = false }) {
  const { loading, user } = useAuth()
  if (loading) return <main className="auth">Checking session…</main>
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && user.role !== 'admin') return <Navigate to="/chat" replace />
  return <Outlet />
}
