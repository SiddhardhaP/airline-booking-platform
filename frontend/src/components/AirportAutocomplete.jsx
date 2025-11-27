import { useState, useEffect, useRef } from 'react'
import client from '../api/client'

export default function AirportAutocomplete({ value, onChange, placeholder, label, required }) {
  const [query, setQuery] = useState(value || '')
  const [suggestions, setSuggestions] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [helperText, setHelperText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const inputRef = useRef(null)
  const dropdownRef = useRef(null)
  const debounceTimerRef = useRef(null)

  // Update query when value prop changes
  useEffect(() => {
    if (value !== query) {
      setQuery(value || '')
    }
  }, [value])

  // Search airports with debouncing
  useEffect(() => {
    // Clear previous timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    // If query is less than 2 characters, clear suggestions
    if (query.length < 2) {
      setSuggestions([])
      setIsOpen(false)
      setHelperText('')
      return
    }

    // Set loading state
    setIsLoading(true)

    // Debounce API call
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const response = await client.get(`/api/flight/airports/search`, {
          params: { query, limit: 10 }
        })
        
        const airports = response.data.airports || []
        setSuggestions(airports)
        setIsOpen(airports.length > 0)
        setSelectedIndex(-1)
        
        // If exact match found or query is a valid 3-letter code, show helper text
        const exactMatch = airports.find(
          a => a.code.toLowerCase() === query.toLowerCase()
        )
        if (exactMatch) {
          setHelperText(`${exactMatch.city} – ${exactMatch.name} (${exactMatch.country})`)
        } else if (query.length === 3 && airports.length > 0) {
          // Show first match's helper text if query is 3 letters
          setHelperText(`${airports[0].city} – ${airports[0].name} (${airports[0].country})`)
        } else {
          setHelperText('')
        }
      } catch (error) {
        console.error('Error searching airports:', error)
        setSuggestions([])
        setIsOpen(false)
        setHelperText('')
      } finally {
        setIsLoading(false)
      }
    }, 400) // 400ms debounce

    // Cleanup
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [query])

  // Handle input change
  const handleInputChange = (e) => {
    const newValue = e.target.value.toUpperCase()
    setQuery(newValue)
    onChange(newValue)
    setIsOpen(true)
  }

  // Handle selection
  const handleSelect = (airport) => {
    setQuery(airport.code)
    onChange(airport.code)
    setIsOpen(false)
    setSuggestions([])
    setHelperText(`${airport.city} – ${airport.name} (${airport.country})`)
    setSelectedIndex(-1)
  }

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!isOpen || suggestions.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault()
      }
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelect(suggestions[selectedIndex])
        } else if (suggestions.length > 0) {
          // Select first suggestion if none selected
          handleSelect(suggestions[0])
        }
        break
      case 'Escape':
        e.preventDefault()
        setIsOpen(false)
        setSelectedIndex(-1)
        break
      default:
        break
    }
  }

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setIsOpen(false)
        setSelectedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0) {
              setIsOpen(true)
            }
          }}
          placeholder={placeholder}
          className="w-full px-3 sm:px-4 py-2.5 sm:py-2 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          required={required}
          maxLength={3}
          autoComplete="off"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
      </div>

      {/* Helper text */}
      {helperText && (
        <p className="mt-1 text-xs text-gray-500">{helperText}</p>
      )}

      {/* Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto"
        >
          {suggestions.map((airport, index) => (
            <div
              key={airport.code}
              onClick={() => handleSelect(airport)}
              className={`px-3 sm:px-4 py-3 min-h-[44px] cursor-pointer hover:bg-primary-50 active:bg-primary-100 transition-colors touch-manipulation ${
                index === selectedIndex ? 'bg-primary-100' : ''
              } ${index === 0 ? 'rounded-t-lg' : ''} ${
                index === suggestions.length - 1 ? 'rounded-b-lg' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-primary-600 text-base sm:text-lg">
                      {airport.code}
                    </span>
                    <span className="text-xs sm:text-sm text-gray-600">
                      {airport.city}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {airport.name} ({airport.country})
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

