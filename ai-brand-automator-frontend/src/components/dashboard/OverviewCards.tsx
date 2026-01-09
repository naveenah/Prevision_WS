export function OverviewCards() {
  const cards = [
    {
      title: 'Total Assets',
      value: '24',
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      title: 'AI Interactions',
      value: '156',
      change: '+23%',
      changeType: 'positive' as const,
    },
    {
      title: 'Automation Tasks',
      value: '8',
      change: '0%',
      changeType: 'neutral' as const,
    },
    {
      title: 'Subscription',
      value: 'Pro',
      change: 'Active',
      changeType: 'neutral' as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500">{card.title}</h3>
          <div className="mt-2 flex items-baseline">
            <p className="text-2xl font-semibold text-gray-900">{card.value}</p>
            <p
              className={`ml-2 text-sm ${
                card.changeType === 'positive'
                  ? 'text-green-600'
                  : 'text-gray-600'
              }`}
            >
              {card.change}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}