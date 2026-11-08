import { motion } from "framer-motion";

const SENTIMENT_CONFIG = {
  positive: { color: "#10b981", glow: "rgba(16,185,129,0.4)", emoji: "😊", label: "Positive" },
  negative: { color: "#ef4444", glow: "rgba(239,68,68,0.4)",  emoji: "😔", label: "Negative" },
  neutral:  { color: "#f59e0b", glow: "rgba(245,158,11,0.4)", emoji: "😐", label: "Neutral" },
};

export default function ConfidenceMeter({ sentiment, confidence }) {
  const cfg = SENTIMENT_CONFIG[sentiment] || SENTIMENT_CONFIG.neutral;
  const pct = Math.round((confidence || 0) * 100);

  return (
    <div className="rounded-2xl p-5"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-4"
        style={{ color: "var(--text-muted)" }}>
        Final Verdict
      </h3>

      {/* Big sentiment display */}
      <div className="flex items-center gap-4 mb-5">
        <motion.div
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ repeat: Infinity, duration: 2.5 }}
          className="text-5xl"
        >
          {cfg.emoji}
        </motion.div>
        <div>
          <div className="text-3xl font-display font-bold" style={{ color: cfg.color }}>
            {cfg.label}
          </div>
          <div className="text-sm mt-0.5" style={{ color: "var(--text-muted)" }}>
            Confidence: {pct}%
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="rounded-full overflow-hidden h-3"
        style={{ background: "rgba(255,255,255,0.06)" }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
          className="h-full rounded-full"
          style={{
            background: `linear-gradient(90deg, ${cfg.color}99, ${cfg.color})`,
            boxShadow: `0 0 12px ${cfg.glow}`,
          }}
        />
      </div>

      {/* Scale labels */}
      <div className="flex justify-between mt-1.5">
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>0%</span>
        <span className="text-xs font-mono font-medium" style={{ color: cfg.color }}>{pct}%</span>
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>100%</span>
      </div>
    </div>
  );
}
