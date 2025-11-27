import { useState, useEffect } from 'react'

const DEFAULT_EMAIL = 'user@example.com'
const STORAGE_KEY = 'userEmail'

/**
 * Custom hook for managing user email from localStorage
 * @param {string} defaultEmail - Default email if none exists
 * @returns {[string, function]} User email and setter function
 */
export function useUserEmail(defaultEmail = DEFAULT_EMAIL) {
  const [userEmail, setUserEmail] = useState(() => {
    // Initialize from localStorage or use default
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEY) || defaultEmail
    }
    return defaultEmail
  })

  useEffect(() => {
    // Save to localStorage whenever email changes
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, userEmail)
    }
  }, [userEmail])

  const updateUserEmail = (newEmail) => {
    setUserEmail(newEmail)
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, newEmail)
    }
  }

  return [userEmail, updateUserEmail]
}

