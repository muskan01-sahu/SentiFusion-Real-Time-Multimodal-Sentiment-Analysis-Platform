import { motion } from "framer-motion";
import { format } from "date-fns";

const SENTIMENT_COLORS = {
  positive: { text: "#10b981", bg: "rgba(16,185,129,0.12)", border: "rgba(16,185,129,0.3)" },
  negative: { text: "#ef4444", bg: "rgba(239,68,68,0.12)",  border: "rgba(239,68,68,0.3)" },
  neutral:  { text: "#f59e0b", bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.3)" },
};

const SENTIMENT_LABELS = {
  positive: "😊 Positive",
  negative: "😔 Negative",
  neutral:  "😐 Neutral",
};

function formatTimestamp(ts) {
  if (!ts) return "";
  try {
    const d = new Date(ts);
    return format(d, "h:mm a · MMM d, yyyy");
  } catch {
    return ts;
  }
}

function formatNumber(n) {
  if (!n) return "0";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

export default function TweetCard({ tweetData, sentiment }) {
  if (!tweetData) return null;

  const sentColor = SENTIMENT_COLORS[sentiment?.final] || SENTIMENT_COLORS.neutral;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-2xl overflow-hidden"
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border-subtle)",
      }}
    >
      {/* Card Header */}
      <div className="px-5 pt-5 pb-4">
        {/* Author row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="w-11 h-11 rounded-full overflow-hidden flex-shrink-0"
              style={{ border: "2px solid rgba(98,114,245,0.3)" }}>
              {tweetData.avatar ? (
                <img src={tweetData.avatar} alt={tweetData.author}
                  className="w-full h-full object-cover"
                  onError={e => { e.target.style.display = "none"; }} />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-xl"
                  style={{ background: "rgba(98,114,245,0.2)" }}>
                  {tweetData.author?.[0] || "?"}
                </div>
              )}
            </div>

            {/* Name + handle */}
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm" style={{ color: "var(--text-primary)" }}>
                  {tweetData.author || "Unknown"}
                </span>
                {tweetData.verified && (
                  <span title="Verified" className="text-blue-400 text-xs">✓</span>
                )}
              </div>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                {tweetData.author_handle || ""}
              </span>
            </div>
          </div>

          {/* Sentiment badge */}
          {sentiment?.final && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring" }}
              className="px-3 py-1 rounded-full text-xs font-semibold flex-shrink-0"
              style={{
                background: sentColor.bg,
                border: `1px solid ${sentColor.border}`,
                color: sentColor.text,
              }}
            >
              {SENTIMENT_LABELS[sentiment.final]}
            </motion.div>
          )}
        </div>

        {/* Tweet text */}
        <div className="mt-4">
          <p className="text-sm leading-relaxed" style={{ color: "var(--text-primary)" }}>
            {tweetData.text || ""}
          </p>
        </div>

        {/* Images */}
        {tweetData.images?.length > 0 && (
          <div className={`mt-3 grid gap-2 ${tweetData.images.length > 1 ? "grid-cols-2" : "grid-cols-1"}`}>
            {tweetData.images.slice(0, 4).map((url, i) => (
              <div key={i} className="rounded-xl overflow-hidden aspect-video bg-white/5">
                <img src={url} alt={`Tweet image ${i + 1}`}
                  className="w-full h-full object-cover"
                  onError={e => { e.target.parentElement.style.display = "none"; }} />
              </div>
            ))}
          </div>
        )}

        {/* Emojis found */}
        {tweetData.emojis?.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {tweetData.emojis.map((em, i) => (
              <span key={i} className="text-xl" title={`Emoji: ${em}`}>{em}</span>
            ))}
          </div>
        )}
      </div>

      {/* Divider */}
      <div style={{ height: "1px", background: "var(--border-subtle)" }} />

      {/* Footer stats */}
      <div className="px-5 py-3 flex items-center gap-5">
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
          {formatTimestamp(tweetData.timestamp)}
        </span>
        <div className="flex items-center gap-4 ml-auto">
          <Stat icon="❤️" value={formatNumber(tweetData.likes)} />
          <Stat icon="🔁" value={formatNumber(tweetData.retweets)} />
          <Stat icon="💬" value={formatNumber(tweetData.replies_count)} />
        </div>
      </div>

      {/* Language + URL */}
      <div className="px-5 pb-4 flex items-center gap-3">
        {tweetData.url && (
          <a href={tweetData.url} target="_blank" rel="noopener noreferrer"
            className="text-xs hover:underline"
            style={{ color: "#6272f5" }}>
            View original →
          </a>
        )}
      </div>
    </motion.div>
  );
}

function Stat({ icon, value }) {
  return (
    <span className="flex items-center gap-1 text-xs" style={{ color: "var(--text-secondary)" }}>
      <span>{icon}</span>
      <span>{value}</span>
    </span>
  );
}
