export function RecentActivity() {
  const activities = [
    {
      id: 1,
      action: 'Uploaded brand logo',
      timestamp: '2 hours ago',
      type: 'upload',
    },
    {
      id: 2,
      action: 'AI generated social media post',
      timestamp: '4 hours ago',
      type: 'ai',
    },
    {
      id: 3,
      action: 'Scheduled content for LinkedIn',
      timestamp: '1 day ago',
      type: 'schedule',
    },
    {
      id: 4,
      action: 'Updated company profile',
      timestamp: '2 days ago',
      type: 'update',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
      </div>
      <div className="divide-y divide-gray-200">
        {activities.map((activity) => (
          <div key={activity.id} className="px-6 py-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-900">{activity.action}</p>
              <p className="text-sm text-gray-500">{activity.timestamp}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}