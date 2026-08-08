export default function MessageBubble({ message }) {
  return (
    <article className={`message ${message.role}`}>
      <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
      <p>{message.content}</p>
      {message.role === 'assistant' && (message.route || message.grade) && (
        <small>Route: {message.route || 'Unknown'} · Grade: {message.grade || 'N/A'}</small>
      )}
    </article>
  )
}
