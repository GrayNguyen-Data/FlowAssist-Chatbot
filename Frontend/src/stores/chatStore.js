import { create } from 'zustand'

const useChatStore = create((set) => ({
  conversations: [],
  activeConvId:  null,
  messages:      [],
  loading:       false,

  setLoading:       (v)    => set({ loading: v }),
  setActiveConv:    (id)   => set({ activeConvId: id, messages: [] }),
  addConversation:  (conv) => set(s => ({ conversations: [conv, ...s.conversations] })),
  setMessages:      (msgs) => set({ messages: msgs }),
  appendMessage:    (msg)  => set(s => ({ messages: [...s.messages, msg] })),
}))

export default useChatStore