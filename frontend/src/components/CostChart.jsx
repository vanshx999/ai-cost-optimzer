import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

export default function CostChart({ stats }) {
  const data = stats?.cost_per_model
    ? Object.entries(stats.cost_per_model).map(([model, cost]) => ({
        name: model,
        cost: parseFloat(cost.toFixed(6)),
      }))
    : [];

  if (!data.length) {
    return (
      <div className="bg-dash-card border border-dash-border rounded-xl p-5">
        <h2 className="text-lg font-semibold text-white mb-1">Cost per Model</h2>
        <p className="text-dash-muted text-sm mb-4">Token spending breakdown</p>
        <p className="text-dash-muted text-sm py-12 text-center">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-dash-card border border-dash-border rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-1">Cost per Model</h2>
      <p className="text-dash-muted text-sm mb-4">Token spending breakdown</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d2d44" />
          <XAxis
            dataKey="name"
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip
            contentStyle={{
              background: '#1a1a2e',
              border: '1px solid #2d2d44',
              borderRadius: 8,
              color: '#e5e7eb',
            }}
            formatter={(v) => [`$${v}`, 'Cost']}
          />
          <Bar
            dataKey="cost"
            fill="#00ff88"
            radius={[6, 6, 0, 0]}
            animationBegin={200}
            animationDuration={800}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
