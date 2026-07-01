import { useEffect, useState } from 'react';
import { checkHealth } from './api';

export default function StatusIndicator() {
  const [ok, setOk] = useState(false);

  const check = () =>
    checkHealth().then(() => setOk(true)).catch(() => setOk(false));

  useEffect(() => {
    check();
    const id = setInterval(check, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex items-center gap-2 text-sm">
      <span
        className={`inline-block w-3 h-3 rounded-full ${ok ? 'bg-green-500 shadow-[0_0_8px_#22c55e]' : 'bg-red-500 shadow-[0_0_8px_#ef4444]'}`}
      />
      <span className="text-dash-muted">API {ok ? 'Online' : 'Offline'}</span>
    </div>
  );
}
