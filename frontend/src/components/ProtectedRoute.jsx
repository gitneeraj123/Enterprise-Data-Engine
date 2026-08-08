import { Navigate, Outlet } from 'react-router-dom'

export default function ProtectedRoute({ adminOnly = false }) {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (!token) return <Navigate to="/login" replace />
  if (adminOnly && role !== 'admin') return <Navigate to="/chat" replace />
  return <Outlet />
}
