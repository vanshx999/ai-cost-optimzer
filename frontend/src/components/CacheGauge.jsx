import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const HIT_RATE = 25.53;
const data = [
  { name: 'Hits', value: HIT_RATE },
  { name: 'Misses', value: 100 - HIT_RATE },
];
const COLORS = ['#00ff88', '#2d2d44'];

export default function CacheGauge() {
  return (
    <div className="bg-dash-card border border-dash-border rounded-xl p-5 flex flex-col items-center justify-center">
      <h2 className="text-lg font-semibold text-white mb-1">Cache Efficiency</h2>
      <p className="text-dash-muted text-sm mb-2">Hit rate performance</p>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            startAngle={90}
            endAngle={-270}
            dataKey="value"
          >
            {data.map((_, idx) => (
              <Cell key={idx} fill={COLORS[idx]} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="text-center -mt-10 mb-2">
        <p className="text-3xl font-bold text-dash-accent">{HIT_RATE}%</p>
        <p className="text-dash-muted text-xs uppercase tracking-wider">Hit Rate</p>
      </div>
      <div className="flex gap-4 text-xs text-dash-muted mt-1">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-dash-accent" /> Hits
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-[#2d2d44]" /> Misses
        </span>
      </div>
    </div>
  );
}
