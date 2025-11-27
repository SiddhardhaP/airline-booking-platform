import { useEffect, useRef } from 'react'

/**
 * Custom hook for auto-scrolling to bottom of a container
 * @param {Array} dependencies - Dependencies that trigger scroll
 * @returns {Object} Ref to attach to the scrollable container
 */
export function useScrollToBottom(dependencies = []) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies)

  return { messagesEndRef, scrollToBottom }
}

