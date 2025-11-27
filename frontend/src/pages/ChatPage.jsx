import { useState } from 'react'
import { useChat, useUserEmail, useScrollToBottom } from '../hooks'

export default function ChatPage() {
  const [input, setInput] = useState('')
  const [userEmail] = useUserEmail()
  const { messages, loading, sendChatMessage } = useChat(userEmail)
  const { messagesEndRef } = useScrollToBottom([messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    await sendChatMessage(userMessage)
  }

  return (
    <div className="max-w-4xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <div className="bg-white rounded-lg shadow-lg h-[calc(100vh-8rem)] sm:h-[600px] flex flex-col">
        <div className="p-3 sm:p-4 border-b">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800">AI Assistant</h1>
          <p className="text-xs sm:text-sm text-gray-500">Ask me anything about flights and bookings</p>
        </div>

        <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-base sm:text-lg">👋 Welcome! How can I help you today?</p>
              <p className="text-xs sm:text-sm mt-2">Ask anything about flights</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-xs lg:max-w-md px-3 sm:px-4 py-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className="text-xs sm:text-sm whitespace-pre-wrap break-words">{msg.text}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 max-w-[85%] sm:max-w-xs lg:max-w-md px-3 sm:px-4 py-2 rounded-lg">
                <p className="text-xs sm:text-sm">Thinking...</p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSend} className="p-3 sm:p-4 border-t">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="min-w-[60px] sm:min-w-[80px] px-4 sm:px-6 py-2 sm:py-2.5 text-sm sm:text-base bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

