import { useLocation, useNavigate } from 'react-router-dom'
import { format } from 'date-fns'

export default function FlightResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const offers = location.state?.offers || []
  const searchParams = location.state?.searchParams || {}

  if (offers.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">No Flights Found</h1>
          <button
            onClick={() => navigate('/search')}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Search Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4 sm:mb-6">Flight Results</h1>

      <div className="space-y-3 sm:space-y-4">
        {offers.map((offer) => (
          <div
            key={offer.offer_id}
            className="bg-white rounded-lg shadow-lg p-4 sm:p-6 hover:shadow-xl transition-shadow"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
              <div className="flex-1 w-full">
                <div className="flex items-center space-x-3 sm:space-x-4 mb-3 sm:mb-4">
                  <div className="text-xl sm:text-2xl font-bold text-primary-600">{offer.airline}</div>
                  <div className="text-sm sm:text-base text-gray-600">{offer.flight_no}</div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-3 sm:mb-4">
                  <div>
                    <p className="text-xs sm:text-sm text-gray-500">Departure</p>
                    <p className="font-semibold text-sm sm:text-base">{offer.origin}</p>
                    <p className="text-xs sm:text-sm text-gray-600">
                      {format(new Date(offer.depart_ts), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs sm:text-sm text-gray-500">Arrival</p>
                    <p className="font-semibold text-sm sm:text-base">{offer.destination}</p>
                    <p className="text-xs sm:text-sm text-gray-600">
                      {format(new Date(offer.arrive_ts), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                </div>

                <div className="text-xs sm:text-sm text-gray-600">
                  <span className="font-semibold">Seats Available:</span> {offer.seats}
                </div>
              </div>

              <div className="w-full sm:w-auto text-left sm:text-right sm:ml-6 border-t sm:border-t-0 pt-4 sm:pt-0">
                <div className="text-2xl sm:text-3xl font-bold text-primary-600 mb-2">
                  {(!offer.currency || offer.currency === 'INR') ? '₹' : '$'}{offer.price.toFixed(2)}
                </div>
                <div className="text-xs sm:text-sm text-gray-500 mb-3 sm:mb-4">{offer.currency || 'INR'}</div>
                <button
                  onClick={() => navigate(`/booking/${offer.offer_id}`)}
                  className="w-full sm:w-auto min-h-[44px] px-6 py-2.5 sm:py-2 text-sm sm:text-base bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Select Flight
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

