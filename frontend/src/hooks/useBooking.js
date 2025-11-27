import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { createBooking, getBooking, getUserBookings, cancelBooking } from '../api/booking'

/**
 * Custom hook for booking operations
 * @param {string} userEmail - User's email address
 * @returns {Object} Booking state and handlers
 */
export function useBooking(userEmail) {
  const queryClient = useQueryClient()

  // Get all bookings for user
  const {
    data: bookings,
    isLoading: isLoadingBookings,
    error: bookingsError,
    refetch: refetchBookings,
  } = useQuery({
    queryKey: ['userBookings', userEmail],
    queryFn: () => getUserBookings(userEmail),
    enabled: !!userEmail,
  })

  // Create booking mutation
  const createBookingMutation = useMutation({
    mutationFn: createBooking,
    onSuccess: () => {
      // Invalidate and refetch bookings after creating a new one
      queryClient.invalidateQueries({ queryKey: ['userBookings', userEmail] })
    },
  })

  // Cancel booking mutation
  const cancelBookingMutation = useMutation({
    mutationFn: cancelBooking,
    onSuccess: (data, bookingId) => {
      // Invalidate and refetch bookings after cancellation
      queryClient.invalidateQueries({ queryKey: ['userBookings', userEmail] })
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] })
    },
  })

  // Get single booking by ID
  const useBookingById = (bookingId) => {
    return useQuery({
      queryKey: ['booking', bookingId],
      queryFn: () => getBooking(bookingId),
      enabled: !!bookingId,
    })
  }

  return {
    bookings: bookings || [],
    isLoadingBookings,
    bookingsError,
    refetchBookings,
    createBooking: createBookingMutation.mutateAsync,
    createBookingLoading: createBookingMutation.isPending,
    createBookingError: createBookingMutation.error,
    cancelBooking: cancelBookingMutation.mutateAsync,
    cancelBookingLoading: cancelBookingMutation.isPending,
    cancelBookingError: cancelBookingMutation.error,
    useBookingById,
  }
}

