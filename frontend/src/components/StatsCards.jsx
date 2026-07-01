export default function StatsCards({ stats }) {
  const cards = [
    {
      label: 'Total Requests',
      value: stats?.total_requests ?? '—',
      icon: (
        <svg className="w-6 h-6 text-dash-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      label: 'Total Cost',
      value: stats?.total_cost != null ? `$${stats.total_cost}` : '—',
      icon: (
        <svg className="w-6 h-6 text-dash-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      label: 'Cache Hit Rate',
      value: '25.53%',
      icon: (
        <svg className="w-6 h-6 text-dash-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="bg-dash-card border border-dash-border rounded-xl p-5 flex items-center gap-4">
          <div className="bg-dash-dark/50 p-3 rounded-lg">{c.icon}</div>
          <div>
            <p className="text-dash-muted text-sm">{c.label}</p>
            <p className="text-2xl font-semibold text-white mt-1">{c.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
