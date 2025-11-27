# Custom Hooks

This directory contains reusable React hooks for the airline booking platform.

## Available Hooks

### `useChat`
Manages chat functionality including messages, loading state, and conversation ID.

**Usage:**
```jsx
import { useChat } from '../hooks'

function ChatPage() {
  const [userEmail] = useUserEmail()
  const { messages, loading, sendChatMessage } = useChat(userEmail)
  
  const handleSend = async (e) => {
    e.preventDefault()
    await sendChatMessage(input)
  }
}
```

### `useUserEmail`
Manages user email from localStorage with automatic persistence.

**Usage:**
```jsx
import { useUserEmail } from '../hooks'

function MyComponent() {
  const [userEmail, setUserEmail] = useUserEmail()
  
  // Email is automatically saved to localStorage
  // and retrieved on component mount
}
```

### `useScrollToBottom`
Auto-scrolls to bottom of a container when dependencies change.

**Usage:**
```jsx
import { useScrollToBottom } from '../hooks'

function ChatPage() {
  const { messages } = useChat()
  const { messagesEndRef } = useScrollToBottom([messages])
  
  return (
    <div>
      {messages.map(...)}
      <div ref={messagesEndRef} />
    </div>
  )
}
```

### `useFlightSearch`
Manages flight search state and operations.

**Usage:**
```jsx
import { useFlightSearch } from '../hooks'

function FlightSearchPage() {
  const {
    searchParams,
    updateSearchParams,
    performSearch,
    offers,
    isLoading
  } = useFlightSearch()
  
  const handleSearch = async () => {
    const data = await performSearch()
    // Navigate to results
  }
}
```

### `useBooking`
Manages booking operations including fetching user bookings and creating new bookings.

**Usage:**
```jsx
import { useBooking } from '../hooks'

function BookingHistoryPage() {
  const [userEmail] = useUserEmail()
  const {
    bookings,
    isLoadingBookings,
    createBooking,
    createBookingLoading
  } = useBooking(userEmail)
  
  const handleCreateBooking = async (bookingData) => {
    const result = await createBooking(bookingData)
    // Handle success
  }
}
```

## Benefits

- **Reusability**: Share logic across multiple components
- **Separation of Concerns**: Business logic separated from UI
- **Testability**: Hooks can be tested independently
- **Cleaner Components**: Components focus on rendering
- **Type Safety**: Can be easily extended with TypeScript

## Example: Refactored ChatPage

See how `ChatPage.jsx` can be simplified using these hooks:

**Before:**
```jsx
const [messages, setMessages] = useState([])
const [loading, setLoading] = useState(false)
const [conversationId, setConversationId] = useState(null)
const [userEmail, setUserEmail] = useState('')
// ... lots of state management code
```

**After:**
```jsx
const [userEmail] = useUserEmail()
const { messages, loading, sendChatMessage } = useChat(userEmail)
const { messagesEndRef } = useScrollToBottom([messages])
// Much cleaner!
```

