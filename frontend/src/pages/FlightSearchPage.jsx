import { useNavigate } from 'react-router-dom'
import { useFlightSearch } from '../hooks'
import AirportAutocomplete from '../components/AirportAutocomplete'

export default function FlightSearchPage() {
  const navigate = useNavigate()
  const {
    searchParams: formData,
    updateSearchParams,
    performSearch,
    offers,
    isLoading,
  } = useFlightSearch()

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = await performSearch()
    if (data && data.offers) {
      navigate('/results', { state: { offers: data.offers, searchParams: formData } })
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
      <div className="bg-white rounded-lg shadow-lg p-4 sm:p-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4 sm:mb-6">Search Flights</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AirportAutocomplete
              value={formData.origin}
              onChange={(value) => updateSearchParams({ origin: value })}
              placeholder="e.g., HYD, Hyderabad, Mumbai"
              label="Origin Airport Code"
              required
            />

            <AirportAutocomplete
              value={formData.destination}
              onChange={(value) => updateSearchParams({ destination: value })}
              placeholder="e.g., BOM, Delhi, Bangalore"
              label="Destination Airport Code"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Departure Date
              </label>
              <input
                type="date"
                value={formData.departure_date}
                onChange={(e) => updateSearchParams({ departure_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Return Date (Optional)
              </label>
              <input
                type="date"
                value={formData.return_date}
                onChange={(e) => updateSearchParams({ return_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Adults</label>
              <input
                type="number"
                value={formData.adults}
                onChange={(e) => updateSearchParams({ adults: parseInt(e.target.value) })}
                min="1"
                max="9"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Children</label>
              <input
                type="number"
                value={formData.children}
                onChange={(e) => updateSearchParams({ children: parseInt(e.target.value) })}
                min="0"
                max="9"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full min-h-[44px] py-3 text-sm sm:text-base bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
          >
            {isLoading ? 'Searching...' : 'Search Flights'}
          </button>
        </form>
      </div>
    </div>
  )
}

