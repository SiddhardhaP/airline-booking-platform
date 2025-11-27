import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getBooking } from '../api/booking'
import { getOfferDetails } from '../api/flight'
import { format } from 'date-fns'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { useUserEmail, useBooking } from '../hooks'
import { useState } from 'react'

export default function BookingConfirmationPage() {
  const { bookingId } = useParams()
  const navigate = useNavigate()
  const [userEmail] = useUserEmail()
  const { cancelBooking, cancelBookingLoading } = useBooking(userEmail)
  const [isCancelling, setIsCancelling] = useState(false)

  const { data: booking, isLoading, refetch } = useQuery({
    queryKey: ['booking', bookingId],
    queryFn: () => getBooking(bookingId),
  })

  const { data: offer } = useQuery({
    queryKey: ['offer', booking?.offer_id],
    queryFn: () => getOfferDetails(booking?.offer_id),
    enabled: !!booking?.offer_id,
  })

  const handleDownloadTicket = () => {
    if (!booking || !offer) return

    // Create ticket HTML content
    const ticketContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Flight Ticket - ${booking.booking_id}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    .ticket {
      background: white;
      border-radius: 10px;
      padding: 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #2563eb;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      color: #2563eb;
      margin: 0;
      font-size: 28px;
    }
    .booking-info {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 30px;
    }
    .info-item {
      margin-bottom: 15px;
    }
    .info-label {
      font-size: 12px;
      color: #666;
      text-transform: uppercase;
      margin-bottom: 5px;
    }
    .info-value {
      font-size: 16px;
      font-weight: bold;
      color: #333;
    }
    .route {
      background: #eff6ff;
      padding: 20px;
      border-radius: 8px;
      margin: 20px 0;
      text-align: center;
    }
    .route-arrow {
      font-size: 24px;
      margin: 10px 0;
    }
    .passengers {
      margin-top: 30px;
      border-top: 2px solid #e5e7eb;
      padding-top: 20px;
    }
    .passenger-item {
      background: #f9fafb;
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 10px;
    }
    .footer {
      text-align: center;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 2px solid #e5e7eb;
      color: #666;
      font-size: 12px;
    }
    .status {
      display: inline-block;
      padding: 5px 15px;
      border-radius: 20px;
      font-weight: bold;
      font-size: 14px;
    }
    .status.confirmed {
      background: #d1fae5;
      color: #065f46;
    }
    .food-service {
      background: #fef3c7;
      padding: 10px;
      border-radius: 5px;
      margin-top: 10px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="ticket">
    <div class="header">
      <h1>✈️ Flight Ticket</h1>
      <p style="margin: 5px 0; color: #666;">Airline Booking Platform</p>
    </div>
    
    <div class="booking-info">
      <div class="info-item">
        <div class="info-label">Booking ID</div>
        <div class="info-value">${booking.booking_id}</div>
      </div>
      <div class="info-item">
        <div class="info-label">Status</div>
        <div class="info-value">
          <span class="status ${booking.status}">${booking.status.toUpperCase()}</span>
        </div>
      </div>
      <div class="info-item">
        <div class="info-label">Flight Number</div>
        <div class="info-value">${offer.airline} ${offer.flight_no}</div>
      </div>
      <div class="info-item">
        <div class="info-label">Date</div>
        <div class="info-value">${format(new Date(offer.depart_ts), 'MMM dd, yyyy')}</div>
      </div>
      <div class="info-item">
        <div class="info-label">Departure Time</div>
        <div class="info-value">${format(new Date(offer.depart_ts), 'HH:mm')}</div>
      </div>
      <div class="info-item">
        <div class="info-label">Arrival Time</div>
        <div class="info-value">${format(new Date(offer.arrive_ts), 'HH:mm')}</div>
      </div>
    </div>

    <div class="route">
      <div style="font-size: 20px; font-weight: bold;">
        ${booking.origin_city ? booking.origin_city : booking.origin} (${booking.origin})
      </div>
      <div class="route-arrow">→</div>
      <div style="font-size: 20px; font-weight: bold;">
        ${booking.destination_city ? booking.destination_city : booking.destination} (${booking.destination})
      </div>
    </div>

    <div class="passengers">
      <h2 style="margin-bottom: 15px; color: #333;">Passengers</h2>
      ${booking.passengers.map((p, idx) => `
        <div class="passenger-item">
          <strong>Passenger ${idx + 1}:</strong> ${p.full_name}<br>
          <small>Email: ${p.email} | Phone: ${p.phone}</small>
          ${p.date_of_birth ? `<br><small>Date of Birth: ${format(new Date(p.date_of_birth), 'MMM dd, yyyy')}</small>` : ''}
        </div>
      `).join('')}
    </div>

    ${booking.food_preference ? `
      <div class="food-service">
        🍽️ Food Service Included
      </div>
    ` : ''}

    <div style="margin-top: 30px; padding: 20px; background: #f0f9ff; border-radius: 8px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 18px; font-weight: bold;">Total Amount:</span>
        <span style="font-size: 24px; font-weight: bold; color: #2563eb;">
          ${booking.currency === 'INR' ? '₹' : '$'}${booking.total_amount.toFixed(2)} ${booking.currency}
        </span>
      </div>
      <div style="margin-top: 10px; font-size: 12px; color: #666;">
        Payment Status: ${booking.payment_status.toUpperCase()}
      </div>
    </div>

    <div class="footer">
      <p>Booking Date: ${format(new Date(booking.created_at), 'MMMM dd, yyyy HH:mm')}</p>
      <p>This is an electronic ticket. Please present this at the airport.</p>
      <p style="margin-top: 10px;">Thank you for choosing our airline!</p>
    </div>
  </div>
</body>
</html>
    `

    // Create blob and download
    const blob = new Blob([ticketContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `ticket-${booking.booking_id}.html`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return
    }

    setIsCancelling(true)
    try {
      await cancelBooking(bookingId)
      await refetch()
      alert('Booking cancelled successfully')
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to cancel booking. Please try again.')
    } finally {
      setIsCancelling(false)
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <LoadingSpinner text="Loading booking details..." />
      </div>
    )
  }

  if (!booking) {
    return <div className="text-center py-8">Booking not found</div>
  }

  return (
    <div className="max-w-4xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <div className="bg-white rounded-lg shadow-lg p-4 sm:p-8">
        <div className="text-center mb-6 sm:mb-8">
          <div className="text-4xl sm:text-6xl mb-3 sm:mb-4">✅</div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">Booking Confirmed!</h1>
          <p className="text-sm sm:text-base text-gray-600">Your flight has been successfully booked</p>
        </div>

        <div className="space-y-4 sm:space-y-6">
          <div className="p-4 sm:p-6 bg-primary-50 rounded-lg">
            <h2 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Booking Details</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
              <div>
                <p className="text-sm text-gray-600">Booking ID</p>
                <p className="font-semibold">{booking.booking_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className={`font-semibold ${
                  booking.status === 'confirmed' ? 'text-green-600' : 
                  booking.status === 'cancelled' ? 'text-red-600' : 
                  'text-gray-600'
                }`}>
                  {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                </p>
              </div>
              {booking.origin && booking.destination && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-600">Route</p>
                  <p className="font-semibold text-lg">
                    {booking.origin_city ? `${booking.origin_city} (${booking.origin})` : booking.origin} → {booking.destination_city ? `${booking.destination_city} (${booking.destination})` : booking.destination}
                  </p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-600">Total Amount</p>
                <p className="font-semibold">
                  {booking.currency === 'INR' ? '₹' : '$'}{booking.total_amount.toFixed(2)} {booking.currency}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Payment Status</p>
                <p className="font-semibold text-green-600">{booking.payment_status}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Booking Date</p>
                <p className="font-semibold">
                  {format(new Date(booking.created_at), 'MMMM dd, yyyy HH:mm')}
                </p>
              </div>
            </div>
          </div>

          <div className="p-6 bg-gray-50 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Passengers</h2>
            <div className="space-y-2">
              {booking.passengers.map((passenger, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{passenger.full_name}</p>
                    <p className="text-sm text-gray-600">{passenger.email}</p>
                  </div>
                  <p className="text-sm text-gray-600">{passenger.phone}</p>
                </div>
              ))}
            </div>
          </div>

          {booking.food_preference && (
            <div className="p-6 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🍽️</span>
                <div>
                  <h2 className="text-xl font-semibold text-green-800">Food Service Selected</h2>
                  <p className="text-sm text-green-600">Meals will be included with your flight</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 sm:mt-8 flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 sm:space-x-4">
          {booking.status === 'confirmed' && (
            <>
              <button
                onClick={handleDownloadTicket}
                disabled={!offer}
                className="w-full sm:w-auto min-h-[44px] px-6 py-3 text-sm sm:text-base bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Ticket
              </button>
              <button
                onClick={handleCancel}
                disabled={isCancelling || cancelBookingLoading}
                className="w-full sm:w-auto min-h-[44px] px-6 py-3 text-sm sm:text-base bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isCancelling || cancelBookingLoading ? 'Cancelling...' : 'Cancel Booking'}
              </button>
            </>
          )}
          <a
            href="/history"
            className="w-full sm:w-auto min-h-[44px] inline-flex items-center justify-center px-6 py-3 text-sm sm:text-base bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            View All Bookings
          </a>
        </div>
      </div>
    </div>
  )
}

