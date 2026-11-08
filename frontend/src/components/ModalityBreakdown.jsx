import { motion } from "framer-motion";

const MODALITY_CONFIG = {
  text:  { icon: "🧠", label: "Text (RoBERTa)", desc: "Transformer-based NLP" },
  emoji: { icon: "😊", label: "Emoji (Lexicon)", desc: "Sentiment lexicon scoring" },
  image: { icon: "🖼️", label: "Image (ViT)",    desc: "Vision Transformer" },
};

const SENTIMENT_COLORS = {
  positive: { color: "#10b981", bg: "rgba(16,185,129,0.12)", glow: "rgba(16,185,129,0.3)" },
  negative: { color: "#ef4444", bg: "rgba(239,68,68,0.12)",  glow: "rgba(239,68,68,0.3)" },
  neutral:  { color: "#f59e0b", bg: "rgba(245,158,11,0.12)", glow: "rgba(245,158,11,0.3)" },
};

export default function ModalityBreakdown({ breakdown, fusionWeights }) {
  if (!breakdown) return null;

  const modalities = ["text", "emoji", "image"];

  return (
    <div className="rounded-2xl p-5"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-4"
        style={{ color: "var(--text-muted)" }}>
        Modality Breakdown
      </h3>

      <div className="space-y-3">
        {modalities.map((key, i) => {
          const mod = breakdown[key];
          if (!mod) return null;
          const cfg    = MODALITY_CONFIG[key];
          const sent   = SENTIMENT_COLORS[mod.label] || SENTIMENT_COLORS.neutral;
          const pct    = Math.round((mod.score || 0) * 100);
          const weight = fusionWeights?.[key] || 0;

          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="rounded-xl p-4"
              style={{
                background: sent.bg,
                border: `1px solid ${sent.glow}`,
              }}
            >
              <div className="flex items-start justify-between mb-2.5">
                <div className="flex items-center gap-2.5">
                  <span className="text-xl">{cfg.icon}</span>
                  <div>
                    <div className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                      {cfg.label}
                    </div>
                    <div className="text-xs" style={{ color: "var(--text-muted)" }}>
                      {cfg.desc}
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm font-bold capitalize" style={{ color: sent.color }}>
                    {mod.label}
                  </div>
                  <div className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                    w={Math.round(weight * 100)}%
                  </div>
                </div>
              </div>

              {/* Score bar */}
              <div className="rounded-full h-1.5 overflow-hidden"
                style={{ background: "rgba(0,0,0,0.2)" }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ duration: 0.8, delay: i * 0.1 + 0.2, ease: "easeOut" }}
                  className="h-full rounded-full"
                  style={{
                    background: sent.color,
                    boxShadow: `0 0 8px ${sent.glow}`,
                  }}
                />
              </div>
              <div className="text-right text-xs mt-1 font-mono" style={{ color: sent.color }}>
                {pct}%
              </div>

              {/* Extra: no image analyzed notice */}
              {key === "image" && mod.analyzed === false && (
                <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                  ⚠️ No image in tweet — modality skipped
                </p>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
