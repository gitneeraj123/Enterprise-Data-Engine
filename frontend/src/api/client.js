const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {})

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || 'Request failed')
  }
  return response.status === 204 ? null : response.json()
}

export function login(username, password) {
  return request('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

export function getCurrentUser() {
  return request('/api/me')
}

export function logout() {
  return request('/api/logout', { method: 'POST' })
}

export function sendChat(query) {
  return request('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
}

export function getDocuments() {
  return request('/api/documents')
}

export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/api/documents/upload', { method: 'POST', body: formData })
}

export function deleteDocument(id) {
  return request(`/api/documents/${id}`, { method: 'DELETE' })
}

export function registerUser(username, password, role = 'employee') {
  return request('/api/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, role }),
  })
}
