import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";

const MODEL_COLORS = ["#6272f5", "#00d4ff", "#8b5cf6"];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="px-3 py-2 rounded-xl text-sm"
      style={{ background: "rgba(15,15,25,0.95)", border: "1px solid rgba(255,255,255,0.1)" }}>
      <p className="font-semibold mb-1" style={{ color: "#f0f0ff" }}>{label}</p>
      <p style={{ color: payload[0].color }}>{(payload[0].value * 100).toFixed(1)}% confidence</p>
    </div>
  );
};

export default function ModelComparisonBar({ modelComparison }) {
  if (!modelComparison) return null;

  const data = Object.entries(modelComparison).map(([model, score]) => ({
    model: model.charAt(0).toUpperCase() + model.slice(1),
    score,
  }));

  return (
    <div className="rounded-2xl p-5"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-4"
        style={{ color: "var(--text-muted)" }}>
        Model Comparison
      </h3>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} barSize={36}>
          <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="model"
            tick={{ fill: "var(--text-secondary)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 1]}
            tickFormatter={v => `${(v * 100).toFixed(0)}%`}
            tick={{ fill: "var(--text-muted)", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
          <Bar dataKey="score" radius={[6, 6, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={MODEL_COLORS[i % MODEL_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
