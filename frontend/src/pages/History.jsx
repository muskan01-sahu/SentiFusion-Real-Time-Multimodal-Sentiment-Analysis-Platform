import { motion } from "framer-motion";
import HistoryPanel from "../components/HistoryPanel";
import { useNavigate } from "react-router-dom";

export default function History() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen pt-24 pb-16 px-4" style={{ background: "var(--bg-primary)" }}>
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="font-display font-bold text-3xl gradient-text">Analysis History</h1>
              <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
                Your past tweet analyses
              </p>
            </div>
            <button
              onClick={() => navigate("/")}
              className="px-4 py-2 rounded-xl text-sm font-medium transition-all hover:scale-105"
              style={{
                background: "linear-gradient(135deg,#6272f5,#8b5cf6)",
                color: "white",
              }}
            >
              + New Analysis
            </button>
          </div>

          <HistoryPanel onSelect={(item) => {
            // Navigate to home with pre-filled URL
            navigate("/", { state: { url: item.tweet_url } });
          }} />
        </motion.div>
      </div>
    </div>
  );
}
