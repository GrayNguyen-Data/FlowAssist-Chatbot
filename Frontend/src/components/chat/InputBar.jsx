import { useState, useRef } from 'react'

export default function InputBar({ onSend, disabled }) {
  const [text, setText] = useState('')
  const taRef           = useRef(null)

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    if (!text.trim() || disabled) return
    onSend(text.trim())
    setText('')
    taRef.current.style.height = 'auto'
  }

  function autoResize(e) {
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px'
  }

  return (
    <div style={{ padding: '12px 20px 16px', borderTop: '1px solid #e5e7eb', background: '#fff' }}>
      <div style={{
        display: 'flex', alignItems: 'flex-end', gap: 8,
        background: '#f9fafb', border: `1.5px solid ${disabled ? '#e5e7eb' : '#d1d5db'}`,
        borderRadius: 10, padding: '8px 10px',
        transition: 'border-color 0.15s',
      }}>
        <textarea
          ref={taRef}
          rows={1}
          value={text}
          onChange={e => { setText(e.target.value); autoResize(e) }}
          onKeyDown={handleKey}
          disabled={disabled}
          placeholder={disabled ? 'Đang trả lời...' : 'Nhập câu hỏi của bạn...'}
          style={{
            flex: 1, background: 'none', border: 'none', outline: 'none',
            fontSize: 14, lineHeight: 1.5, resize: 'none',
            maxHeight: 140, fontFamily: 'inherit', color: '#1a1a1a',
          }}
        />
        <button
          onClick={submit}
          disabled={disabled || !text.trim()}
          style={{
            width: 34, height: 34, borderRadius: 7, border: 'none',
            background: disabled || !text.trim() ? '#e5e7eb' : '#1a1a1a',
            color: '#fff', cursor: disabled ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0, fontSize: 16, transition: 'background 0.12s',
          }}
        >
          ↑
        </button>
      </div>
      <div style={{ fontSize: 11, color: '#9ca3af', textAlign: 'right', marginTop: 4 }}>
        Enter gửi · Shift+Enter xuống dòng
      </div>
    </div>
  )
}