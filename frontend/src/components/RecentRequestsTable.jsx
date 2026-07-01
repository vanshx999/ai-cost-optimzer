const ROWS = [
  { id: 1, user: 'vansh', model: 'llama3-8b-8192', tokens: 42, cost: 0.000042, cached: false, time: '2 min ago' },
  { id: 2, user: 'vansh', model: 'llama3-8b-8192', tokens: 128, cost: 0.000128, cached: true, time: '5 min ago' },
  { id: 3, user: 'friend', model: 'llama3-8b-8192', tokens: 64, cost: 0.000064, cached: false, time: '12 min ago' },
  { id: 4, user: 'vansh', model: 'llama3-8b-8192', tokens: 256, cost: 0.000256, cached: false, time: '18 min ago' },
  { id: 5, user: 'friend', model: 'llama3-8b-8192', tokens: 16, cost: 0.000016, cached: true, time: '25 min ago' },
];

export default function RecentRequestsTable() {
  return (
    <div className="bg-dash-card border border-dash-border rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Recent Requests</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-dash-muted border-b border-dash-border">
              <th className="text-left pb-3 font-medium">User</th>
              <th className="text-left pb-3 font-medium">Model</th>
              <th className="text-right pb-3 font-medium">Tokens</th>
              <th className="text-right pb-3 font-medium">Cost</th>
              <th className="text-center pb-3 font-medium">Cached</th>
              <th className="text-right pb-3 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map((r) => (
              <tr key={r.id} className="border-b border-dash-border/50 last:border-0 hover:bg-white/[0.02]">
                <td className="py-3 text-white">{r.user}</td>
                <td className="py-3 text-gray-300">{r.model}</td>
                <td className="py-3 text-right text-gray-300">{r.tokens.toLocaleString()}</td>
                <td className="py-3 text-right text-gray-300">${r.cost.toFixed(6)}</td>
                <td className="py-3 text-center">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                      r.cached
                        ? 'bg-green-900/50 text-green-400'
                        : 'bg-gray-700/50 text-gray-400'
                    }`}
                  >
                    {r.cached ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="py-3 text-right text-dash-muted">{r.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
