import { format } from 'date-fns'
import { Link } from 'react-router-dom'
import { useUserEmail, useBooking } from '../hooks'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { useState } from 'react'

export default function BookingHistoryPage() {
  const [userEmail] = useUserEmail()
  const { bookings, isLoadingBookings: isLoading, cancelBooking, cancelBookingLoading, refetchBookings } = useBooking(userEmail)
  const [cancellingId, setCancellingId] = useState(null)

  const handleCancel = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return
    }

    setCancellingId(bookingId)
    try {
      await cancelBooking(bookingId)
      await refetchBookings()
      alert('Booking cancelled successfully')
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to cancel booking. Please try again.')
    } finally {
      setCancellingId(null)
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <LoadingSpinner text="Loading bookings..." />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4 sm:mb-6">My Bookings</h1>

      {!bookings || bookings.length === 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <p className="text-gray-600 mb-4">No bookings found</p>
          <Link
            to="/search"
            className="inline-block px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Search Flights
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.booking_id} className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start gap-3 sm:gap-0 mb-4">
                <div className="flex-1">
                  <h3 className="text-lg sm:text-xl font-semibold">Booking {booking.booking_id}</h3>
                  <p className="text-xs sm:text-sm text-gray-600">
                    {format(new Date(booking.created_at), 'MMMM dd, yyyy')}
                  </p>
                  {booking.origin && booking.destination && (
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">
                      {booking.origin_city ? `${booking.origin_city} (${booking.origin})` : booking.origin} → {booking.destination_city ? `${booking.destination_city} (${booking.destination})` : booking.destination}
                    </p>
                  )}
                </div>
                <div className="w-full sm:w-auto text-left sm:text-right">
                  <p className="text-xl sm:text-2xl font-bold text-primary-600">
                    {booking.currency === 'INR' ? '₹' : '$'}{booking.total_amount.toFixed(2)} {booking.currency}
                  </p>
                  <p
                    className={`text-xs sm:text-sm font-semibold ${
                      booking.status === 'confirmed' ? 'text-green-600' : 
                      booking.status === 'cancelled' ? 'text-red-600' : 
                      'text-gray-600'
                    }`}
                  >
                    {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                  </p>
                </div>
              </div>

              <div className="border-t pt-4">
                <h4 className="font-semibold mb-2">Passengers</h4>
                <div className="space-y-1">
                  {booking.passengers.map((passenger, idx) => (
                    <div key={idx} className="text-sm text-gray-600">
                      {passenger.full_name} - {passenger.email}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
                <Link
                  to={`/confirmation/${booking.booking_id}`}
                  className="text-center sm:text-left text-primary-600 hover:text-primary-700 text-sm font-semibold py-2 sm:py-0"
                >
                  View Details →
                </Link>
                {booking.status === 'confirmed' && (
                  <button
                    onClick={() => handleCancel(booking.booking_id)}
                    disabled={cancellingId === booking.booking_id || cancelBookingLoading}
                    className="w-full sm:w-auto min-h-[44px] px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {cancellingId === booking.booking_id || cancelBookingLoading ? 'Cancelling...' : 'Cancel'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

