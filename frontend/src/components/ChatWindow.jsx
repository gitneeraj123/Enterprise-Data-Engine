import { useState } from 'react'
import { sendChat } from '../api/client'
import MessageBubble from './MessageBubble'

export default function ChatWindow() {
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed || loading) return
    setMessages((history) => [...history, { role: 'user', content: trimmed }])
    setQuery('')
    setError('')
    setLoading(true)
    try {
      const response = await sendChat(trimmed)
      setMessages((history) => [...history, {
        role: 'assistant', content: response.answer, route: response.route, grade: response.grade,
      }])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="chat-window">
      <div className="messages">
        {messages.length === 0 && <p className="muted">Ask about company policies or employee data.</p>}
        {messages.map((message, index) => <MessageBubble key={index} message={message} />)}
        {loading && <p className="muted">Thinking…</p>}
      </div>
      {error && <p className="error">{error}</p>}
      <form onSubmit={submit} className="chat-form">
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask a question" />
        <button disabled={loading}>Send</button>
      </form>
    </section>
  )
}
