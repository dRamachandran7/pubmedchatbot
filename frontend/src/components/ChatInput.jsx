import { useState, useRef } from 'react'
import '../styles/ChatInput.css'

function ChatInput({ onSendMessage, isLoading }) {
  const [inputValue, setInputValue] = useState('')
  const inputRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue)
      setInputValue('')
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <input
          ref={inputRef}
          type="text"
          className="chat-input"
          placeholder="Ask a question about medical research..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          autoFocus
        />
        <button type="submit" className="send-button" disabled={isLoading || !inputValue.trim()}>
          {isLoading ? (
            <span className="loading-spinner">⏳</span>
          ) : (
            <span className="send-icon">➤</span>
          )}
        </button>
      </div>
      <p className="input-hint">Press Shift+Enter for new line, Enter to send</p>
    </form>
  )
}

export default ChatInput
