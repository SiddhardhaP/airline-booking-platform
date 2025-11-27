import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchFlights } from '../api/flight'

/**
 * Custom hook for flight search functionality
 * @param {Object} initialSearchParams - Initial search parameters
 * @returns {Object} Search state and handlers
 */
export function useFlightSearch(initialSearchParams = {}) {
  const [searchParams, setSearchParams] = useState({
    origin: '',
    destination: '',
    departure_date: '',
    return_date: '',
    adults: 1,
    children: 0,
    infants: 0,
    ...initialSearchParams,
  })

  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['flightSearch', searchParams],
    queryFn: () => searchFlights(searchParams),
    enabled: false, // Don't auto-fetch, wait for manual trigger
  })

  const updateSearchParams = useCallback((updates) => {
    setSearchParams((prev) => ({ ...prev, ...updates }))
  }, [])

  const resetSearchParams = useCallback(() => {
    setSearchParams({
      origin: '',
      destination: '',
      departure_date: '',
      return_date: '',
      adults: 1,
      children: 0,
      infants: 0,
    })
  }, [])

  const performSearch = useCallback(async () => {
    const result = await refetch()
    return result.data
  }, [refetch])

  return {
    searchParams,
    updateSearchParams,
    resetSearchParams,
    performSearch,
    offers: data?.offers || [],
    count: data?.count || 0,
    isLoading: isLoading || isFetching,
    error,
  }
}

