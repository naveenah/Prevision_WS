'use client';

import { ChatInterface } from '@/components/chat/ChatInterface';
import { useAuth } from '@/hooks/useAuth';

export default function ChatPage() {
  useAuth(); // Protect this route
  return (
    <div className="h-screen bg-brand-midnight">
      <ChatInterface />
    </div>
  );
}