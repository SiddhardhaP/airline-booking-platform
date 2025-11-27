import client from './client'

export const sendMessage = async (message, userEmail, conversationId = null) => {
  const response = await client.post('/api/chat/message', {
    message,
    user_email: userEmail,
    conversation_id: conversationId,
  })
  return response.data
}

