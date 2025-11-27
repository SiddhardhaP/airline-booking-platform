import client from './client'

export const createBooking = async (bookingData) => {
  const response = await client.post('/api/booking/simulate_confirm', bookingData)
  return response.data
}

export const getBooking = async (bookingId) => {
  const response = await client.get(`/api/booking/${bookingId}`)
  return response.data
}

export const getUserBookings = async (userEmail) => {
  const response = await client.get(`/api/booking/user/${userEmail}`)
  return response.data
}

export const cancelBooking = async (bookingId) => {
  const response = await client.post(`/api/booking/${bookingId}/cancel`)
  return response.data
}

