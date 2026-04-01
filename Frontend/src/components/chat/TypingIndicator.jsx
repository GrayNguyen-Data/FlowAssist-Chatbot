export default function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: 4, padding: '8px 16px' }}>
      {[0, 1, 2].map(i => (
        <span key={i} style={{
          width: 6, height: 6, borderRadius: '50%',
          background: '#888', display: 'inline-block',
          animation: `bounce 1.2s infinite`,
          animationDelay: `${i * 0.2}s`,
        }}/>
      ))}
      <style>{`@keyframes bounce{0%,80%,100%{transform:scale(0.7);opacity:0.4}40%{transform:scale(1);opacity:1}}`}</style>
    </div>
  )
}