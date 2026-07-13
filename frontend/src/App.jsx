import { useEffect, useState, useCallback } from 'react';
import { fetchStats } from './components/api';
import StatusIndicator from './components/StatusIndicator';
import StatsCards from './components/StatsCards';
import CostChart from './components/CostChart';
import RecentRequestsTable from './components/RecentRequestsTable';
import CacheGauge from './components/CacheGauge';

function Skeleton({ className }) {
  return <div className={`animate-pulse rounded-lg bg-dash-border/50 ${className}`} />;
}

export default function App() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const load = useCallback(() => {
    fetchStats()
      .then((data) => {
        setStats(data);
        setLastRefreshed(new Date());
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 30000);
    return () => clearInterval(id);
  }, [load]);

  return (
    <div className="min-h-screen bg-dash-dark">
      <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fadeIn">
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
              AI Cost Optimizer
            </h1>
            <p className="text-dash-muted text-sm mt-1">
              Monitor your LLM usage & spending
              {lastRefreshed && (
                <span className="ml-2">
                  &middot; Updated {lastRefreshed.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
          <StatusIndicator />
        </header>

        {loading ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
            </div>
            <Skeleton className="h-[320px]" />
            <Skeleton className="h-[280px]" />
          </div>
        ) : (
          <div className="space-y-6">
            <StatsCards stats={stats} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <CostChart stats={stats} />
              </div>
              <CacheGauge />
            </div>
            <RecentRequestsTable />
          </div>
        )}
      </div>
    </div>
  );
}
