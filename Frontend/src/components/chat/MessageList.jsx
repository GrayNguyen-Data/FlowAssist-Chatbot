import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'

export default function MessageList({ messages, loading }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: '20px 0' }}>
      {messages.map(msg => (
        <MessageBubble
          key={msg.message_id}
          role={msg.role}
          content={msg.content}
          messageId={msg.message_id}
          contexts={msg.retrieved_context ?? []}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}