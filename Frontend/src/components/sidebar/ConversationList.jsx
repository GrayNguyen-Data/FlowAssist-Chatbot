import useChatStore from '../../stores/chatStore'
import { getMessages } from '../../api/chatAPI'

export default function ConversationList() {
  const { conversations, activeConvId, setActiveConv, setMessages } = useChatStore()

  async function handleSelect(convId) {
    setActiveConv(convId)
    const msgs = await getMessages(convId)
    setMessages(msgs)
  }

  if (!conversations.length) {
    return (
      <div style={{ padding: 16, fontSize: 12, color: '#9ca3af', textAlign: 'center' }}>
        Chưa có hội thoại nào
      </div>
    )
  }

  return (
    <div style={{ flex: 1, overflowY: 'auto' }}>
      {conversations.map(conv => (
        <div
          key={conv.conversation_id}
          onClick={() => handleSelect(conv.conversation_id)}
          style={{
            padding: '9px 12px', cursor: 'pointer', fontSize: 13,
            borderRadius: 6, margin: '2px 8px',
            background: conv.conversation_id === activeConvId ? '#f0f4ff' : 'transparent',
            color:      conv.conversation_id === activeConvId ? '#2563eb' : '#374151',
            fontWeight: conv.conversation_id === activeConvId ? 500 : 400,
            transition: 'background 0.1s',
          }}
        >
          {conv.title ?? 'Hội thoại'}
        </div>
      ))}
    </div>
  )
}