import { forwardRef, useEffect, useRef } from 'react'
import Message from './Message'
import '../styles/MessageList.css'

const MessageList = forwardRef(({ messages }, ref) => {
  const innerRef = useRef(null)

  const scrollToBottom = () => {
    if (innerRef.current) {
      innerRef.current.scrollTop = innerRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Expose scrollToBottom to parent
  if (ref) {
    ref.current = { scrollToBottom }
  }

  return (
    <div className="message-list" ref={innerRef}>
      {messages.length === 0 ? (
        <div className="empty-state">
          <p>No messages yet. Start by asking a question!</p>
        </div>
      ) : (
        messages.map((message) => <Message key={message.id} message={message} />)
      )}
    </div>
  )
})

MessageList.displayName = 'MessageList'

export default MessageList
