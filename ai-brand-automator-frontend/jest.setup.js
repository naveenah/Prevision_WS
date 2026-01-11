// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Create a proper localStorage mock with actual storage
let store = {}

const createLocalStorageMock = () => ({
  getItem: jest.fn((key) => store[key] || null),
  setItem: jest.fn((key, value) => {
    store[key] = value.toString()
  }),
  removeItem: jest.fn((key) => {
    delete store[key]
  }),
  clear: jest.fn(() => {
    store = {}
  }),
})

global.localStorage = createLocalStorageMock()

// Mock fetch globally
global.fetch = jest.fn()

// Reset mocks before each test
beforeEach(() => {
  // Clear all mock call history
  jest.clearAllMocks()
  
  // Reset localStorage store and recreate mocks
  store = {}
  global.localStorage = createLocalStorageMock()
  
  // Clear fetch mock
  global.fetch.mockClear()
})
