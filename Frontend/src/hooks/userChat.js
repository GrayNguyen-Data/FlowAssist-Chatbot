import useChatStore from '../stores/chatStore'
import { createConversation, sendMessage, getMessages } from '../api/chatAPI'

export function useChat() {
  const {
    conversations, activeConvId, messages, loading,
    setLoading, setActiveConv, addConversation, setMessages, appendMessage,
  } = useChatStore()

  async function startConversation(userId = 'user_01', title = null) {
    const conv = await createConversation(userId, title)
    addConversation(conv)
    setActiveConv(conv.conversation_id)
    return conv
  }

  async function selectConversation(convId) {
    setActiveConv(convId)
    const msgs = await getMessages(convId)
    setMessages(msgs)
  }

  async function send(text) {
    if (!activeConvId || loading || !text.trim()) return
    setLoading(true)
    appendMessage({ role: 'user', content: text, message_id: Date.now() })
    try {
      const res = await sendMessage(activeConvId, text)
      const msgs = await getMessages(activeConvId)
      setMessages(msgs)
    } catch (err) {
      appendMessage({ role: 'assistant', content: '⚠️ Lỗi: ' + err.message, message_id: Date.now() })
    } finally {
      setLoading(false)
    }
  }

  return { conversations, activeConvId, messages, loading, startConversation, selectConversation, send }
}