import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { LoginForm } from '@/components/auth/LoginForm'
import { RegisterForm } from '@/components/auth/RegisterForm'
import { CompanyForm } from '@/components/onboarding/CompanyForm'
import { BrandForm } from '@/components/onboarding/BrandForm'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { apiClient } from '@/lib/api'

// Mock API client
jest.mock('@/lib/api', () => ({
  apiClient: {
    post: jest.fn(),
    put: jest.fn(),
    get: jest.fn(),
  },
}))

// Mock router
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}))

describe('Integration Tests: User Flows', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    window.localStorage.clear()
    mockPush.mockClear()
  })

  describe('Registration → Login Flow', () => {
    it('allows user to register and then login', async () => {
      // Step 1: Register new user
      const registerResponse = {
        ok: true,
        json: async () => ({
          tokens: {
            access: 'register-token',
            refresh: 'register-refresh',
          },
          user: { id: 1, email: 'newuser@example.com' },
        }),
      }
      
      global.fetch = jest.fn().mockResolvedValueOnce(registerResponse)
      window.alert = jest.fn()
      
      const { unmount } = render(<RegisterForm />)
      
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: 'newuser@example.com' },
      })
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: 'SecurePass123!' },
      })
      fireEvent.change(screen.getByLabelText(/confirm password/i), {
        target: { value: 'SecurePass123!' },
      })
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: 'John' },
      })
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: 'Doe' },
      })
      
      fireEvent.click(screen.getByRole('button', { name: /sign up/i }))
      
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe('register-token')
        expect(mockPush).toHaveBeenCalledWith('/onboarding/step-1')
      }, { timeout: 3000 })
      
      unmount()
      localStorage.clear()
      
      // Step 2: Login with same credentials
      const loginResponse = {
        ok: true,
        json: async () => ({
          tokens: {
            access: 'login-token',
            refresh: 'login-refresh',
          },
        }),
      }
      
      ;(apiClient.post as jest.Mock).mockResolvedValue(loginResponse)
      
      render(<LoginForm />)
      
      fireEvent.change(screen.getByLabelText(/email address/i), {
        target: { value: 'newuser@example.com' },
      })
      fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: 'SecurePass123!' },
      })
      
      fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(apiClient.post).toHaveBeenCalledWith('/auth/login/', {
          email: 'newuser@example.com',
          password: 'SecurePass123!',
        })
      }, { timeout: 3000 })
    })
  })

  describe('Full Onboarding Flow', () => {
    it('completes company creation successfully', async () => {
      localStorage.setItem('access_token', 'test-token')
      
      // Mock window.alert
      window.alert = jest.fn()
      
      // Step 1: Create company
      const companyResponse = {
        ok: true,
        json: async () => ({
          id: '456',
          name: 'Integration Test Co',
          industry: 'technology',
        }),
      }
      
      ;(apiClient.post as jest.Mock).mockResolvedValue(companyResponse)
      
      render(<CompanyForm />)
      
      fireEvent.change(screen.getByLabelText(/name/i), {
        target: { value: 'Integration Test Co' },
      })
      fireEvent.change(screen.getByLabelText(/industry/i), {
        target: { value: 'technology' },
      })
      fireEvent.change(screen.getByLabelText(/description/i), {
        target: { value: 'A test company for integration testing' },
      })
      fireEvent.change(screen.getByLabelText(/target audience/i), {
        target: { value: 'Tech professionals' },
      })
      fireEvent.change(screen.getByLabelText(/core problem/i), {
        target: { value: 'A test company for integration testing' },
      })
      
      fireEvent.click(screen.getByRole('button', { name: /next/i }))
      
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/onboarding/step-2')
        expect(localStorage.getItem('company_id')).toBe('456')
      }, { timeout: 3000 })
    })
  })

  describe('AI Chat Interaction Flow', () => {
    it('sends message and receives AI response', async () => {
      localStorage.setItem('access_token', 'test-token')
      
      const chatResponse = {
        ok: true,
        json: async () => ({
          session_id: 'session-123',
          response: 'Hello! How can I help you with your brand today?',
        }),
      }
      
      ;(apiClient.post as jest.Mock).mockResolvedValue(chatResponse)
      
      render(<ChatInterface />)
      
      // Find input and send button
      const input = screen.getByPlaceholderText(/ask me about your brand/i)
      const sendButton = screen.getByRole('button', { name: /send/i })
      
      // Type and send message
      fireEvent.change(input, {
        target: { value: 'Help me with brand strategy' },
      })
      fireEvent.click(sendButton)
      
      // Verify message was sent
      await waitFor(() => {
        expect(apiClient.post).toHaveBeenCalledWith('/ai/chat/', {
          message: 'Help me with brand strategy',
        })
      }, { timeout: 3000 })
      
      // Verify AI response appears
      await waitFor(() => {
        expect(screen.getByText(/how can i help you/i)).toBeInTheDocument()
      }, { timeout: 3000 })
      
      // Verify input was cleared
      expect(input).toHaveValue('')
    })

    it('handles multiple message exchanges', async () => {
      localStorage.setItem('access_token', 'test-token')
      
      const responses = [
        {
          ok: true,
          json: async () => ({
            session_id: 'session-123',
            response: 'I can help you with that!',
          }),
        },
        {
          ok: true,
          json: async () => ({
            session_id: 'session-123',
            response: 'Here are some suggestions...',
          }),
        },
      ]
      
      ;(apiClient.post as jest.Mock)
        .mockResolvedValueOnce(responses[0])
        .mockResolvedValueOnce(responses[1])
      
      render(<ChatInterface />)
      
      const input = screen.getByPlaceholderText(/ask me about your brand/i)
      const sendButton = screen.getByRole('button', { name: /send/i })
      
      // First message
      fireEvent.change(input, { target: { value: 'Hello' } })
      fireEvent.click(sendButton)
      
      await waitFor(() => {
        expect(screen.getByText(/i can help you/i)).toBeInTheDocument()
      }, { timeout: 3000 })
      
      // Second message
      fireEvent.change(input, { target: { value: 'Tell me more' } })
      fireEvent.click(sendButton)
      
      await waitFor(() => {
        expect(screen.getByText(/here are some suggestions/i)).toBeInTheDocument()
      }, { timeout: 3000 })
      
      // Verify both messages are displayed
      expect(screen.getByText(/i can help you/i)).toBeInTheDocument()
      expect(screen.getByText(/here are some suggestions/i)).toBeInTheDocument()
    })
  })

  describe('Error Recovery Flow', () => {
    it('recovers from failed company creation and retries', async () => {
      localStorage.setItem('access_token', 'test-token')
      
      // Mock window.alert
      const alertMock = jest.fn()
      window.alert = alertMock
      
      // First attempt fails
      const errorResponse = {
        ok: false,
        json: async () => ({
          detail: 'Company name already exists',
        }),
      }
      
      // Second attempt succeeds
      const successResponse = {
        ok: true,
        json: async () => ({
          id: '789',
          name: 'Unique Company Name',
          industry: 'technology',
        }),
      }
      
      ;(apiClient.post as jest.Mock)
        .mockResolvedValueOnce(errorResponse)
        .mockResolvedValueOnce(successResponse)
      
      render(<CompanyForm />)
      
      // First attempt
      fireEvent.change(screen.getByLabelText(/name/i), {
        target: { value: 'Duplicate Name' },
      })
      fireEvent.change(screen.getByLabelText(/industry/i), {
        target: { value: 'technology' },
      })
      fireEvent.change(screen.getByLabelText(/description/i), {
        target: { value: 'Test description' },
      })
      fireEvent.change(screen.getByLabelText(/target audience/i), {
        target: { value: 'Tech users' },
      })
      fireEvent.change(screen.getByLabelText(/core problem/i), {
        target: { value: 'Test problem' },
      })
      fireEvent.click(screen.getByRole('button', { name: /next/i }))
      
      await waitFor(() => {
        expect(alertMock).toHaveBeenCalledWith('Company name already exists')
      }, { timeout: 3000 })
      
      expect(mockPush).not.toHaveBeenCalled()
      
      // Second attempt with different name
      fireEvent.change(screen.getByLabelText(/name/i), {
        target: { value: 'Unique Company Name' },
      })
      fireEvent.click(screen.getByRole('button', { name: /next/i }))
      
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/onboarding/step-2')
      }, { timeout: 3000 })
    })
  })
})
