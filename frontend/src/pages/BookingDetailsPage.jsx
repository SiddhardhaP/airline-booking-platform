import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getOfferDetails } from '../api/flight'

export default function BookingDetailsPage() {
  const { offerId } = useParams()
  const navigate = useNavigate()
  const [passengers, setPassengers] = useState([
    { full_name: '', email: '', phone: '', date_of_birth: '', passport_number: '' },
  ])
  const [foodPreference, setFoodPreference] = useState(false)

  const { data: offer, isLoading } = useQuery({
    queryKey: ['offer', offerId],
    queryFn: () => getOfferDetails(offerId),
  })

  const addPassenger = () => {
    setPassengers([...passengers, { full_name: '', email: '', phone: '', date_of_birth: '', passport_number: '' }])
  }

  const updatePassenger = (index, field, value) => {
    const updated = [...passengers]
    updated[index][field] = value
    setPassengers(updated)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    navigate(`/payment/${offerId}`, { state: { passengers, offer, foodPreference } })
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (!offer) {
    return <div className="text-center py-8">Offer not found</div>
  }

  return (
    <div className="max-w-4xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <div className="bg-white rounded-lg shadow-lg p-4 sm:p-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4 sm:mb-6">Passenger Details</h1>

        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h2 className="font-semibold mb-2">Selected Flight</h2>
          <p>
            {offer.airline} {offer.flight_no} - {offer.currency === 'INR' ? '₹' : '$'}{offer.price.toFixed(2)} {offer.currency}
          </p>
          <p className="text-sm text-gray-600">
            {offer.origin} → {offer.destination}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {passengers.map((passenger, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Passenger {index + 1}</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={passenger.full_name}
                    onChange={(e) => updatePassenger(index, 'full_name', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                  <input
                    type="email"
                    value={passenger.email}
                    onChange={(e) => updatePassenger(index, 'email', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Phone *</label>
                  <input
                    type="tel"
                    value={passenger.phone}
                    onChange={(e) => updatePassenger(index, 'phone', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date of Birth *
                  </label>
                  <input
                    type="date"
                    value={passenger.date_of_birth}
                    onChange={(e) => updatePassenger(index, 'date_of_birth', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Passport Number
                  </label>
                  <input
                    type="text"
                    value={passenger.passport_number}
                    onChange={(e) => updatePassenger(index, 'passport_number', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            </div>
          ))}

          <button
            type="button"
            onClick={addPassenger}
            className="px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50"
          >
            + Add Another Passenger
          </button>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={foodPreference}
                onChange={(e) => setFoodPreference(e.target.checked)}
                className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span className="text-sm font-medium text-gray-700">
                I would like to include food service
              </span>
            </label>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 sm:space-x-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="w-full sm:flex-1 min-h-[44px] px-6 py-3 text-sm sm:text-base border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back
            </button>
            <button
              type="submit"
              className="w-full sm:flex-1 min-h-[44px] px-6 py-3 text-sm sm:text-base bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Continue to Payment
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

