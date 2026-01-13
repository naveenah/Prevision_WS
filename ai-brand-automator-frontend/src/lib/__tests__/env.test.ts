import { env } from '@/lib/env'

describe('env configuration', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  it('has default API URL', () => {
    expect(env.apiUrl).toBe('http://localhost:8000')
  })

  it('uses environment variable for API URL when provided', async () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com'
    const { env: newEnv } = await import('@/lib/env')
    expect(newEnv.apiUrl).toBe('https://api.example.com')
  })

  it('constructs full API URL correctly', () => {
    const url = env.getApiUrl('/companies/')
    expect(url).toBe('http://localhost:8000/api/v1/companies/')
  })

  it('handles paths without leading slash', () => {
    const url = env.getApiUrl('companies/')
    expect(url).toBe('http://localhost:8000/api/v1/companies/')
  })

  it('returns base URL when no path provided', () => {
    const url = env.getApiUrl()
    expect(url).toBe('http://localhost:8000/api/v1')
  })

  it('correctly identifies development environment', async () => {
    const originalEnv = process.env.NODE_ENV
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'development',
      writable: true,
      configurable: true
    })
    const { env: newEnv } = await import('@/lib/env')
    expect(newEnv.isDevelopment).toBe(true)
    expect(newEnv.isProduction).toBe(false)
    
    // Restore original value
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: originalEnv,
      writable: true,
      configurable: true
    })
  })

  it('correctly identifies production environment', async () => {
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'production',
      writable: true,
      configurable: true
    })
    const { env: newEnv } = await import('@/lib/env')
    expect(newEnv.isDevelopment).toBe(false)
    expect(newEnv.isDevelopment).toBe(false)
    expect(newEnv.isProduction).toBe(true)
  })

  it('validates configuration', () => {
    const result = env.validate()
    expect(result).toBe(true)
  })

  it('detects missing API URL in validation', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    
    const testEnv = {
      ...env,
      apiUrl: '',
    }
    
    const result = testEnv.validate()
    expect(result).toBe(false)
    
    consoleSpy.mockRestore()
  })
})
