import { useEffect, useState } from 'react';
import { checkHealth } from './api';

export default function StatusIndicator() {
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(true);

  const check = () =>
    checkHealth()
      .then(() => { setOk(true); })
      .catch(() => { setOk(false); })
      .finally(() => setLoading(false));

  useEffect(() => {
    check();
    const id = setInterval(check, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex items-center gap-3 bg-dash-card border border-dash-border rounded-lg px-4 py-2.5">
      {loading ? (
        <div className="w-3 h-3 rounded-full bg-dash-muted animate-pulse" />
      ) : (
        <span
          className={`inline-block w-3 h-3 rounded-full transition-all duration-500 ${
            ok
              ? 'bg-emerald-500 shadow-[0_0_12px_#10b981] animate-pulse'
              : 'bg-red-500 shadow-[0_0_12px_#ef4444]'
          }`}
        />
      )}
      <div className="flex flex-col">
        <span className={`text-xs font-medium ${ok ? 'text-emerald-400' : 'text-red-400'}`}>
          {loading ? 'Checking...' : ok ? 'API Online' : 'API Offline'}
        </span>
        <span className="text-[10px] text-dash-muted">
          {loading ? '' : ok ? 'All systems normal' : 'Connection error'}
        </span>
      </div>
    </div>
  );
}
