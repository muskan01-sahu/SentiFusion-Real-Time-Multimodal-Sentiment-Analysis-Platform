import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral:  "#f59e0b",
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const { name, value } = payload[0];
  return (
    <div className="px-3 py-2 rounded-xl text-sm"
      style={{ background: "rgba(15,15,25,0.95)", border: "1px solid rgba(255,255,255,0.1)" }}>
      <span className="capitalize font-semibold" style={{ color: COLORS[name] }}>{name}</span>
      <span className="ml-2" style={{ color: "#f0f0ff" }}>{(value * 100).toFixed(1)}%</span>
    </div>
  );
};

const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  if (percent < 0.07) return null;
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central"
      fontSize={12} fontWeight={600}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default function SentimentPieChart({ scores }) {
  if (!scores) return null;

  const data = Object.entries(scores).map(([name, value]) => ({ name, value }));

  return (
    <div className="rounded-2xl p-5"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-4"
        style={{ color: "var(--text-muted)" }}>
        Sentiment Distribution
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%" cy="50%"
            innerRadius={55} outerRadius={85}
            dataKey="value"
            labelLine={false}
            label={CustomLabel}
            strokeWidth={0}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || "#888"} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(val) => (
              <span className="capitalize text-xs" style={{ color: "var(--text-secondary)" }}>{val}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
