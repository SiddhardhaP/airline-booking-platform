import { useState, useCallback } from 'react'
import { sendMessage } from '../api/chat'

/**
 * Custom hook for managing chat functionality
 * @param {string} userEmail - User's email address
 * @returns {Object} Chat state and handlers
 */
export function useChat(userEmail) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [error, setError] = useState(null)

  const sendChatMessage = useCallback(
    async (message) => {
      if (!message.trim() || loading) return

      const userMessage = message.trim()
      setMessages((prev) => [...prev, { role: 'user', text: userMessage }])
      setLoading(true)
      setError(null)

      try {
        const response = await sendMessage(userMessage, userEmail, conversationId)
        setConversationId(response.conversation_id)
        setMessages((prev) => [...prev, { role: 'assistant', text: response.response }])
        return response
      } catch (err) {
        const errorMessage = 'Sorry, I encountered an error. Please try again.'
        setMessages((prev) => [...prev, { role: 'assistant', text: errorMessage }])
        setError(err.message || errorMessage)
        throw err
      } finally {
        setLoading(false)
      }
    },
    [userEmail, conversationId, loading]
  )

  const clearMessages = useCallback(() => {
    setMessages([])
    setConversationId(null)
    setError(null)
  }, [])

  return {
    messages,
    loading,
    error,
    conversationId,
    sendChatMessage,
    clearMessages,
  }
}

