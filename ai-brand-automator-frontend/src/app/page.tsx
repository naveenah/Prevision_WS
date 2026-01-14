'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (token) {
      // Redirect to dashboard if authenticated
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-brand-midnight">
      {/* Aura glow effect */}
      <div className="fixed inset-0 aura-glow pointer-events-none" />
      
      {/* Header */}
      <header className="relative z-10 px-4 sm:px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <h1 className="text-xl sm:text-2xl font-heading font-bold text-white">AI Brand Automator</h1>
          <div className="flex items-center gap-2 sm:gap-4">
            <Link
              href="/auth/login"
              className="text-brand-silver hover:text-brand-electric px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/auth/register"
              className="btn-primary text-sm whitespace-nowrap"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        <div className="text-center">
          <h1 className="text-3xl sm:text-4xl md:text-6xl font-heading font-bold text-white mb-4 sm:mb-6">
            Automate Your Brand
            <span className="text-brand-electric block">with AI Power</span>
          </h1>
          <p className="text-base sm:text-xl text-brand-silver/80 mb-6 sm:mb-8 max-w-3xl mx-auto font-body px-2">
            Streamline your brand management with AI-driven insights, automated social media posting,
            and intelligent content generation. Build a stronger brand presence effortlessly.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <Link
              href="/auth/register"
              className="btn-primary text-base sm:text-lg w-full sm:w-auto text-center"
            >
              Start Free Trial
            </Link>
            <Link
              href="/auth/login"
              className="btn-secondary text-base sm:text-lg w-full sm:w-auto text-center"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 sm:mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          <div className="glass-card p-6 sm:p-8 text-center group hover:border-brand-electric/50 transition-colors">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-brand-electric/20 transition-colors">
              <span className="text-2xl">🤖</span>
            </div>
            <h3 className="text-lg sm:text-xl font-heading font-semibold text-white mb-2">AI-Powered Insights</h3>
            <p className="text-sm sm:text-base text-brand-silver/70 font-body">
              Get intelligent recommendations for your brand strategy and content creation.
            </p>
          </div>
          <div className="glass-card p-6 sm:p-8 text-center group hover:border-brand-electric/50 transition-colors">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-brand-electric/20 transition-colors">
              <span className="text-2xl">📅</span>
            </div>
            <h3 className="text-lg sm:text-xl font-heading font-semibold text-white mb-2">Automated Scheduling</h3>
            <p className="text-sm sm:text-base text-brand-silver/70 font-body">
              Schedule and automate your social media posts across all platforms.
            </p>
          </div>
          <div className="glass-card p-6 sm:p-8 text-center group hover:border-brand-electric/50 transition-colors">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-brand-ghost/20 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-brand-electric/20 transition-colors">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg sm:text-xl font-heading font-semibold text-white mb-2">Brand Analytics</h3>
            <p className="text-sm sm:text-base text-brand-silver/70 font-body">
              Track your brand performance and engagement across all channels.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 mt-12 sm:mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="text-center text-brand-silver/60 font-body text-sm sm:text-base">
            <p>&copy; 2026 AI Brand Automator. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
