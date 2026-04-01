import api from "./axios";

export async function createConversation({
  userId = "default",
  title = "New conversation",
  channel = "chat",
} = {}) {
  const response = await api.post("/conversations", {
    user_id: userId,
    title,
    channel,
  });
  return response.data;
}

export async function getConversationMessages(conversationId) {
  const response = await api.get(`/conversations/${conversationId}/messages`);
  return response.data;
}

export async function sendChatMessage({ conversationId, message }) {
  const response = await api.post("/chat", {
    conversation_id: conversationId,
    message,
  });
  return response.data;
}

export async function submitFeedback(payload) {
  const response = await api.post("/feedback", payload);
  return response.data;
}

export default {
  createConversation,
  getConversationMessages,
  sendChatMessage,
  submitFeedback,
};