import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatPage from './pages/ChatPage'
import FlightSearchPage from './pages/FlightSearchPage'
import FlightResultsPage from './pages/FlightResultsPage'
import BookingDetailsPage from './pages/BookingDetailsPage'
import PaymentPage from './pages/PaymentPage'
import BookingConfirmationPage from './pages/BookingConfirmationPage'
import BookingHistoryPage from './pages/BookingHistoryPage'
import Navbar from './components/Navbar'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/search" element={<FlightSearchPage />} />
            <Route path="/results" element={<FlightResultsPage />} />
            <Route path="/booking/:offerId" element={<BookingDetailsPage />} />
            <Route path="/payment/:offerId" element={<PaymentPage />} />
            <Route path="/confirmation/:bookingId" element={<BookingConfirmationPage />} />
            <Route path="/history" element={<BookingHistoryPage />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App

