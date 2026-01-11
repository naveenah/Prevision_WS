import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { RegisterForm } from '@/components/auth/RegisterForm'

// Create mock router
const mockPush = jest.fn()

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}))

describe('RegisterForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    window.localStorage.clear()
    mockPush.mockClear()
    global.fetch = jest.fn()
  })

  it('renders registration form with all required fields', () => {
    render(<RegisterForm />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument()
  })

  it('validates required fields', () => {
    render(<RegisterForm />)
    
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password$/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const firstNameInput = screen.getByLabelText(/first name/i)
    
    expect(emailInput).toBeRequired()
    expect(passwordInput).toBeRequired()
    expect(confirmPasswordInput).toBeRequired()
    expect(firstNameInput).toBeRequired()
  })

  it('validates email format', () => {
    render(<RegisterForm />)
    
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement
    expect(emailInput.type).toBe('email')
  })

  it('shows error when passwords do not match', async () => {
    render(<RegisterForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'different123' },
    })
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'Test' },
    })
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'User' },
    })
    
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))
    
    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
    })
  })

  it('submits registration with valid data', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: { id: 1, email: 'test@example.com' },
      }),
    }
    
    ;(global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse)
    
    render(<RegisterForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
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
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register/'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'SecurePass123!',
            first_name: 'John',
            last_name: 'Doe',
          }),
        })
      )
    })
  })

  it('stores tokens and redirects after successful registration', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        tokens: {
          access: 'new-access-token',
          refresh: 'new-refresh-token',
        }
      }),
    }
    
    ;(global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse)
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem')
    window.alert = jest.fn()
    
    render(<RegisterForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'new@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'Jane' },
    })
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'Smith' },
    })
    
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))
    
    await waitFor(() => {
      expect(setItemSpy).toHaveBeenCalledWith('access_token', 'new-access-token')
      expect(setItemSpy).toHaveBeenCalledWith('refresh_token', 'new-refresh-token')
      expect(mockPush).toHaveBeenCalledWith('/onboarding/step-1')
    }, { timeout: 3000 })
    
    setItemSpy.mockRestore()
  })

  it('handles registration errors', async () => {
    const mockResponse = {
      ok: false,
      json: async () => ({
        email: ['A user with this email already exists.'],
      }),
    }
    
    ;(global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse)
    
    render(<RegisterForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'existing@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'Test' },
    })
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'User' },
    })
    
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))
    
    await waitFor(() => {
      expect(screen.getByText(/Registration failed/i)).toBeInTheDocument()
    })
  })

  it('disables submit button while loading', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        tokens: {
          access: 'token',
          refresh: 'token',
        }
      }),
    }
    
    ;(global.fetch as jest.Mock).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockResponse), 100))
    )
    
    window.alert = jest.fn()
    
    render(<RegisterForm />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    })
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'password123' },
    })
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'Test' },
    })
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'User' },
    })
    
    const submitButton = screen.getByRole('button', { name: /sign up/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(submitButton).toBeDisabled()
    })
    
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/onboarding/step-1')
    }, { timeout: 3000 })
  })

  it('has link to login page', () => {
    render(<RegisterForm />)
    
    const loginLink = screen.getByText(/already have an account/i).closest('a')
    expect(loginLink).toHaveAttribute('href', '/auth/login')
  })
})
