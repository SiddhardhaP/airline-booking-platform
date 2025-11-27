import { useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useUserEmail, useBooking } from '../hooks'

export default function PaymentPage() {
  const { offerId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { passengers, offer, foodPreference = false } = location.state || {}
  const [userEmail] = useUserEmail()
  const { createBooking, createBookingLoading: loading } = useBooking(userEmail)

  useEffect(() => {
    if (!passengers || !offer) {
      navigate('/search')
    }
  }, [passengers, offer, navigate])

  if (!passengers || !offer) {
    return null
  }

  const baseAmount = offer.price * passengers.length
  const foodCharge = foodPreference ? (offer.currency === 'INR' ? 200 : 200 / 83) : 0
  const totalAmount = baseAmount + foodCharge

  const handlePayment = async () => {
    try {
      const booking = await createBooking({
        offer_id: offerId,
        user_email: userEmail,
        passengers: passengers.map((p) => ({
          full_name: p.full_name,
          email: p.email,
          phone: p.phone,
          date_of_birth: p.date_of_birth,
          passport_number: p.passport_number || null,
        })),
        food_preference: foodPreference,
      })
      navigate(`/confirmation/${booking.booking_id}`)
    } catch (error) {
      alert('Payment failed. Please try again.')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <div className="bg-white rounded-lg shadow-lg p-4 sm:p-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4 sm:mb-6">Payment</h1>

        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h2 className="font-semibold mb-2">Flight Details</h2>
          <p>
            {offer.airline} {offer.flight_no}
          </p>
          <p className="text-sm text-gray-600">
            {offer.origin} → {offer.destination}
          </p>
        </div>

        <div className="mb-6">
          <h2 className="font-semibold mb-4">Passengers</h2>
          <div className="space-y-2">
            {passengers.map((p, idx) => (
              <div key={idx} className="text-sm text-gray-600">
                {p.full_name} ({p.email})
              </div>
            ))}
          </div>
        </div>

        <div className="mb-6 p-4 bg-primary-50 rounded-lg space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm sm:text-base text-gray-700">Flight Charges:</span>
            <span className="text-sm sm:text-base font-semibold">
              {offer.currency === 'INR' ? '₹' : '$'}{baseAmount.toFixed(2)} {offer.currency}
            </span>
          </div>
          {foodPreference && (
            <div className="flex justify-between items-center">
              <span className="text-sm sm:text-base text-gray-700">Food Service:</span>
              <span className="text-sm sm:text-base font-semibold">
                {offer.currency === 'INR' ? '₹' : '$'}{foodCharge.toFixed(2)} {offer.currency}
              </span>
            </div>
          )}
          <div className="flex justify-between items-center pt-2 border-t border-primary-200">
            <span className="text-lg font-semibold">Total Amount:</span>
            <span className="text-2xl font-bold text-primary-600">
              {offer.currency === 'INR' ? '₹' : '$'}{totalAmount.toFixed(2)} {offer.currency}
            </span>
          </div>
        </div>

        <div className="mb-6 p-4 border-2 border-dashed border-gray-300 rounded-lg text-center">
          <p className="text-gray-600 mb-2">This is a simulated payment</p>
          <p className="text-sm text-gray-500">No real payment will be processed</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 sm:space-x-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="w-full sm:flex-1 min-h-[44px] px-6 py-3 text-sm sm:text-base border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading}
          >
            Back
          </button>
          <button
            onClick={handlePayment}
            disabled={loading}
            className="w-full sm:flex-1 min-h-[44px] px-6 py-3 text-sm sm:text-base bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Processing...' : 'Confirm Payment'}
          </button>
        </div>
      </div>
    </div>
  )
}

