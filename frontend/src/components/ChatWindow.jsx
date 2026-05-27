import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import '../styles/ChatWindow.css'

function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: 'Hello! I\'m your PubMed research assistant. Ask me any questions about medical research, and I\'ll help you find relevant articles.',
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messageListRef = useRef(null)

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollToBottom()
    }
  }, [messages])

  const handleSendMessage = async (userMessage) => {
    // Add user message
    const newUserMessage = {
      id: messages.length + 1,
      type: 'user',
      text: userMessage,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newUserMessage])
    setIsLoading(true)

    try {
      console.log('📤 Sending to backend:', { query: userMessage, sessionId: 'default' })
      
      const response = await fetch('http://localhost:4000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          sessionId: 'default',
        }),
      })

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('📥 Received from backend:', data)

      const assistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: data.message,
        timestamp: new Date(),
        sources: data.sources || [],
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('❌ Error:', error)
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: `Error: ${error.message}. Make sure the backend is running on http://localhost:4000`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h1>PubMed Research Assistant</h1>
        <p className="header-subtitle">Ask questions about medical research</p>
      </div>
      <MessageList ref={messageListRef} messages={messages} />
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  )
}

export default ChatWindow
