import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import AdminDashboard from './pages/AdminDashboard'
import Chat from './pages/Chat'
import Login from './pages/Login'

export default function App() {
  return <BrowserRouter><Routes>
    <Route path="/login" element={<Login />} />
    <Route element={<ProtectedRoute />}><Route path="/chat" element={<Chat />} /></Route>
    <Route element={<ProtectedRoute adminOnly />}><Route path="/admin" element={<AdminDashboard />} /></Route>
    <Route path="*" element={<Navigate to="/chat" replace />} />
  </Routes></BrowserRouter>
}
