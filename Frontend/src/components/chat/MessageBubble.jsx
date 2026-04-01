import { useState } from 'react'
import { submitFeedback } from '../../api/chatAPI'
import useChatStore from '../../stores/chatStore'

export default function MessageBubble({ role, content, messageId, contexts = [] }) {
  const [fbSent, setFbSent]     = useState(false)
  const { activeConvId }        = useChatStore()
  const isBot                   = role === 'assistant'

  async function sendFeedback(rating) {
    if (fbSent || !messageId) return
    try {
      await submitFeedback({ conversation_id: activeConvId, message_id: messageId, rating })
      setFbSent(true)
    } catch (err) {
      console.error('Feedback failed', err)
    }
  }

  return (
    <div className={`bubble-row ${isBot ? 'assistant-row' : 'user-row'}`}>
      <div className="bubble-avatar" style={{background: isBot ? '#eef2ff' : '#111827', color: isBot ? '#2563eb' : '#fff'}}>
        {isBot ? 'FA' : 'U'}
      </div>

      <div className="bubble-content">
        <div className={`bubble ${isBot ? 'assistant' : 'user'}`}>
          {content}
        </div>

        {isBot && contexts.length > 0 && (
          <div className="bubble-contexts">
            {contexts.map((c, i) => (
              <span key={i} className="context-pill">{c.slice(0, 50)}…</span>
            ))}
          </div>
        )}

        {isBot && messageId && (
          <div className="feedback-row">
            {fbSent ? (
              <span style={{ fontSize: 12, color: '#6b7280' }}>✓ Đã gửi</span>
            ) : (
              <>
                <button className="btn-feedback" onClick={() => sendFeedback(1)}>👍</button>
                <button className="btn-feedback" onClick={() => sendFeedback(0)}>👎</button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

const btnStyle = {
  padding: '3px 10px', fontSize: 12, cursor: 'pointer',
  background: 'none', border: '1px solid #e5e7eb',
  borderRadius: 4, color: '#6b7280',
}