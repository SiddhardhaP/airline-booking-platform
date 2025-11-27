import client from './client'

export const searchFlights = async (searchParams) => {
  const response = await client.post('/api/flight/search', searchParams)
  return response.data
}

export const getOfferDetails = async (offerId) => {
  const response = await client.get(`/api/flight/offer/${offerId}`)
  return response.data
}

