import { motion } from "framer-motion";

function scoreToColor(score) {
  if (score === undefined || score === null) return "#888";
  if (score > 0.3)  return "#10b981"; // positive
  if (score < -0.3) return "#ef4444"; // negative
  return "#f59e0b";                    // neutral
}

function scoreToLabel(score) {
  if (score > 0.3)  return "positive";
  if (score < -0.3) return "negative";
  return "neutral";
}

export default function EmojiVisualizer({ emojiScores, emojisFound }) {
  const hasEmojis = emojisFound?.length > 0;

  return (
    <div className="rounded-2xl p-5"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-4"
        style={{ color: "var(--text-muted)" }}>
        Emoji Sentiment
      </h3>

      {!hasEmojis ? (
        <p className="text-sm text-center py-4" style={{ color: "var(--text-muted)" }}>
          No emojis detected in this tweet
        </p>
      ) : (
        <div className="space-y-2.5">
          {Object.entries(emojiScores || {}).map(([emoji, score], i) => {
            const color = scoreToColor(score);
            const pct   = Math.abs(score) * 100;
            const label = scoreToLabel(score);

            return (
              <motion.div
                key={emoji}
                initial={{ opacity: 0, x: -15 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.07 }}
                className="flex items-center gap-3"
              >
                <span className="text-2xl w-9 text-center flex-shrink-0">{emoji}</span>

                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-xs capitalize" style={{ color }}>{label}</span>
                    <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                      {pct.toFixed(0)}%
                    </span>
                  </div>
                  <div className="rounded-full h-1.5 overflow-hidden"
                    style={{ background: "rgba(255,255,255,0.06)" }}>
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(pct, 100)}%` }}
                      transition={{ duration: 0.6, delay: i * 0.07 + 0.2 }}
                      className="h-full rounded-full"
                      style={{ background: color, boxShadow: `0 0 8px ${color}66` }}
                    />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
