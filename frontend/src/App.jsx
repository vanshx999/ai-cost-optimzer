import { useEffect, useState } from 'react';
import { fetchStats } from './components/api';
import StatusIndicator from './components/StatusIndicator';
import StatsCards from './components/StatsCards';
import CostChart from './components/CostChart';
import RecentRequestsTable from './components/RecentRequestsTable';

export default function App() {
  const [stats, setStats] = useState(null);

  const load = () =>
    fetchStats().then(setStats).catch(() => {});

  useEffect(() => {
    load();
    const id = setInterval(load, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-dash-dark p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              AI Cost Optimizer
            </h1>
            <p className="text-dash-muted text-sm mt-1">Monitor your LLM usage & spending</p>
          </div>
          <StatusIndicator />
        </header>

        <div className="space-y-6">
          <StatsCards stats={stats} />
          <CostChart stats={stats} />
          <RecentRequestsTable />
        </div>
      </div>
    </div>
  );
}
