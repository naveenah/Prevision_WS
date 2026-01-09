import Link from 'next/link';

export function QuickActions() {
  const actions = [
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
      title: 'View Reports',
      description: 'Analyze your brand performance',
      href: '/reports',
      icon: '📊',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
      </div>
      <div className="p-6 space-y-4">
        {actions.map((action, index) => (
          <Link
            key={index}
            href={action.href}
            className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center">
              <span className="text-2xl mr-3">{action.icon}</span>
              <div>
                <h4 className="text-sm font-medium text-gray-900">{action.title}</h4>
                <p className="text-sm text-gray-500">{action.description}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}