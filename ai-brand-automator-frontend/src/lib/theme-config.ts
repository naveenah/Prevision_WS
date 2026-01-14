/**
 * AI Brand Automator Theme Configuration
 * "Digital Twilight" Design System
 * 
 * This file serves as the source of truth for the design system.
 * Copilot: Reference these tokens when styling components.
 */

export const theme = {
  colors: {
    brand: {
      midnight: '#0A0B10',  // Deep background
      electric: '#00F5FF',  // Primary CTAs / AI Spark
      ghost: '#8A2BE2',     // Accent / Secondary gradients
      silver: '#E1E1E6',    // Primary text
      mint: '#39FF14',      // Success / Automated states
    },
    // Opacity variants for common use cases
    opacity: {
      ghostLight: 'rgba(138, 43, 226, 0.1)',   // Subtle ghost overlay
      ghostMedium: 'rgba(138, 43, 226, 0.3)',  // Hover states
      electricGlow: 'rgba(0, 245, 255, 0.5)', // Button glow
      silverMuted: 'rgba(225, 225, 230, 0.7)', // Secondary text
    },
  },
  
  fonts: {
    heading: 'var(--font-heading)',
    body: 'var(--font-sans)',
    mono: 'var(--font-mono)',
  },
  
  gradients: {
    auraGlow: 'radial-gradient(circle at center, rgba(138,43,226,0.15) 0%, transparent 70%)',
    glassCard: 'linear-gradient(110deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
    electricShimmer: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.2), transparent)',
  },
  
  shadows: {
    glow: '0 0 20px rgba(0, 245, 255, 0.5)',
    card: '0 4px 30px rgba(0, 0, 0, 0.1)',
    elevated: '0 8px 40px rgba(0, 0, 0, 0.3)',
  },
  
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '1rem',
    xl: '1.5rem',
    full: '9999px',
  },
  
  transitions: {
    fast: '150ms ease',
    normal: '300ms ease',
    slow: '500ms ease',
  },
} as const;

// CSS class names for components
export const componentClasses = {
  // Cards
  glassCard: 'glass-card',
  
  // Buttons
  btnPrimary: 'btn-primary',
  btnSecondary: 'btn-secondary',
  
  // Effects
  aiPulse: 'ai-pulse',
  auraGlow: 'aura-glow',
  
  // Status
  statusActive: 'status-active',
} as const;

// Tailwind class presets for common patterns
export const tailwindPresets = {
  // Text colors
  textPrimary: 'text-brand-silver',
  textSecondary: 'text-brand-silver/70',
  textHeading: 'text-white font-heading',
  textAccent: 'text-brand-electric',
  textSuccess: 'text-brand-mint',
  
  // Backgrounds
  bgPrimary: 'bg-brand-midnight',
  bgCard: 'glass-card',
  
  // Interactive states
  hoverGlow: 'hover:shadow-[0_0_20px_rgba(0,245,255,0.5)]',
  hoverBorder: 'hover:border-brand-electric/50',
  
  // Common patterns
  cardPadding: 'p-6',
  sectionSpacing: 'py-12 md:py-20',
  containerPadding: 'px-4 md:px-6 lg:px-8',
} as const;

export type ThemeColors = typeof theme.colors;
export type ThemeFonts = typeof theme.fonts;
