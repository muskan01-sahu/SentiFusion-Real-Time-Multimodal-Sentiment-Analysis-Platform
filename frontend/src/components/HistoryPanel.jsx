import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { formatDistanceToNow } from "date-fns";
import { getHistory, deleteAnalysis } from "../utils/api";
import toast from "react-hot-toast";

const SENTIMENT_COLORS = {
  positive: "#10b981",
  negative: "#ef4444",
  neutral:  "#f59e0b",
};

const SENTIMENT_EMOJIS = {
  positive: "😊",
  negative: "😔",
  neutral:  "😐",
};

export default function HistoryPanel({ onSelect }) {
  const [items, setItems]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getHistory(20);
      setItems(data.items || []);
    } catch (e) {
      setError("Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await deleteAnalysis(id);
      setItems(prev => prev.filter(i => i.id !== id));
      toast.success("Deleted");
    } catch {
      toast.error("Failed to delete");
    }
  };

  if (loading) return (
    <div className="space-y-3">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-20 rounded-xl shimmer-bg" />
      ))}
    </div>
  );

  if (error) return (
    <p className="text-sm py-8 text-center" style={{ color: "var(--text-muted)" }}>{error}</p>
  );

  if (!items.length) return (
    <div className="text-center py-12">
      <div className="text-4xl mb-3">📭</div>
      <p className="text-sm" style={{ color: "var(--text-muted)" }}>No analyses yet</p>
      <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
        Analyze a tweet to see it here
      </p>
    </div>
  );

  return (
    <div className="space-y-2">
      <AnimatePresence>
        {items.map((item, i) => (
          <motion.div
            key={item.id}
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ delay: i * 0.04 }}
            onClick={() => onSelect?.(item)}
            className="rounded-xl px-4 py-3 cursor-pointer group transition-all hover:scale-[1.01]"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
            }}
          >
            <div className="flex items-start gap-3">
              <span className="text-xl mt-0.5 flex-shrink-0">
                {SENTIMENT_EMOJIS[item.final_sentiment] || "😐"}
              </span>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-semibold capitalize"
                    style={{ color: SENTIMENT_COLORS[item.final_sentiment] || "#888" }}>
                    {item.final_sentiment}
                  </span>
                  <span className="text-xs font-mono"
                    style={{ color: "var(--text-muted)" }}>
                    {Math.round((item.confidence || 0) * 100)}%
                  </span>
                  {item.sarcasm_detected && (
                    <span className="text-xs px-1.5 py-0.5 rounded"
                      style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b" }}>
                      ⚠️ sarcasm
                    </span>
                  )}
                </div>

                <p className="text-xs truncate" style={{ color: "var(--text-secondary)" }}>
                  {item.tweet_text || item.tweet_url}
                </p>

                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                    {item.tweet_author || ""}
                  </span>
                  <span className="text-xs" style={{ color: "var(--text-muted)" }}>·</span>
                  <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                    {item.created_at
                      ? formatDistanceToNow(new Date(item.created_at), { addSuffix: true })
                      : ""}
                  </span>
                </div>
              </div>

              {/* Delete button */}
              <button
                onClick={(e) => handleDelete(item.id, e)}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-xs px-2 py-1 rounded-lg flex-shrink-0"
                style={{ color: "#ef4444", background: "rgba(239,68,68,0.1)" }}
              >
                ✕
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
