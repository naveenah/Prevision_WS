import Link from 'next/link';

export function QuickActions() {
  const actions = [
    {
      title: 'Company Onboarding',
      description: 'Set up your company profile and brand strategy',
      href: '/onboarding',
      icon: '🚀',
    },
    {
      title: 'Chat with AI',
      description: 'Get brand insights and generate content',
      href: '/chat',
      icon: '💬',
    },
    {
      title: 'Upload Files',
      description: 'Add brand assets and documents',
      href: '/files',
      icon: '📁',
    },
    {
      title: 'Schedule Content',
      description: 'Plan and automate social media posts',
      href: '/automation',
      icon: '📅',
    },
    {
      title: 'Subscription Plans',
      description: 'View and upgrade your subscription',
      href: '/subscription',
      icon: '⭐',
    },
    {
      title: 'Billing',
      description: 'Manage payments and invoices',
      href: '/billing',
      icon: '💳',
    },
  ];

  return (
    <div className="dashboard-card">
      <div className="mb-4">
        <h3 className="text-lg font-heading font-medium text-white">Quick Actions</h3>
      </div>
      <div className="space-y-3">
        {actions.map((action, index) => (
          <Link
            key={index}
            href={action.href}
            className="block p-4 rounded-lg border border-white/10 hover:bg-white/5 hover:border-brand-electric/30 transition-all"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">{action.icon}</span>
              <div>
                <h4 className="text-sm font-medium text-white">{action.title}</h4>
                <p className="text-sm text-brand-silver/60">{action.description}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}