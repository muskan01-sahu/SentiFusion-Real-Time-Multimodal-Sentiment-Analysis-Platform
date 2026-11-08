import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast, { Toaster } from "react-hot-toast";
import { useAnalysis } from "../hooks/useAnalysis";
import LoadingSteps from "../components/LoadingSteps";
import TweetCard from "../components/TweetCard";
import SentimentDashboard from "../components/SentimentDashboard";

const EXAMPLE_URLS = [
  "https://twitter.com/elonmusk/status/1234567890",
  "https://x.com/NASA/status/9876543210",
  "https://twitter.com/OpenAI/status/1122334455",
];

const DEMO_URL_HINT = "Paste any Twitter/X URL to analyze";

export default function Home() {
  const [url, setUrl] = useState("");
  const { status, result, error, currentStep, steps, analyze, reset } = useAnalysis();

  const handleSubmit = async () => {
    const trimmed = url.trim();
    if (!trimmed) {
      toast.error("Please enter a tweet URL");
      return;
    }
    if (!trimmed.includes("twitter.com") && !trimmed.includes("x.com")) {
      toast.error("Please enter a valid Twitter/X URL");
      return;
    }
    await analyze(trimmed);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  const handleReset = () => {
    reset();
    setUrl("");
  };

  return (
    <div className="min-h-screen pt-20 pb-16 px-4" style={{ background: "var(--bg-primary)" }}>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "rgba(15,15,25,0.95)",
            color: "#f0f0ff",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "12px",
            backdropFilter: "blur(20px)",
          },
        }}
      />

      {/* Background orbs */}
      <div className="orb w-96 h-96 top-20 -left-32"
        style={{ background: "radial-gradient(circle, rgba(98,114,245,0.3) 0%, transparent 70%)" }} />
      <div className="orb w-80 h-80 top-40 right-0"
        style={{ background: "radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)" }} />
      <div className="orb w-64 h-64 bottom-32 left-1/3"
        style={{ background: "radial-gradient(circle, rgba(0,212,255,0.15) 0%, transparent 70%)" }} />

      <div className="relative z-10 max-w-6xl mx-auto">

        {/* ── Hero Section ────────────────────────────────────────── */}
        <AnimatePresence>
          {status === "idle" && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.6 }}
              className="text-center mb-12"
            >
              {/* Badge */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6 text-xs font-medium"
                style={{
                  background: "rgba(98,114,245,0.12)",
                  border: "1px solid rgba(98,114,245,0.3)",
                  color: "#8599f9",
                }}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Final Year B.Tech Project · Deep Learning + Transformers
              </motion.div>

              {/* Headline */}
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="font-display font-extrabold text-4xl sm:text-5xl md:text-6xl leading-tight mb-4"
              >
                <span style={{ color: "var(--text-primary)" }}>Multimodal</span>
                <br />
                <span className="gradient-text">Sentiment Analysis</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-base sm:text-lg max-w-xl mx-auto mb-3"
                style={{ color: "var(--text-secondary)" }}
              >
                Analyze tweet sentiment using BERT, Vision Transformers, and Emoji AI —
                all fused into one prediction.
              </motion.p>

              {/* Model badges */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="flex flex-wrap justify-center gap-2 text-xs"
              >
                {["RoBERTa", "ViT", "Emoji2Vec", "Multimodal Fusion", "Sarcasm Detection"].map(m => (
                  <span key={m} className="px-2.5 py-1 rounded-full"
                    style={{
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      color: "var(--text-muted)",
                    }}>
                    {m}
                  </span>
                ))}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── URL Input ──────────────────────────────────────────── */}
        {(status === "idle" || status === "error") && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="max-w-2xl mx-auto mb-8"
          >
            <div className="rounded-2xl p-1.5 flex gap-2"
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(98,114,245,0.3)",
                boxShadow: "0 0 30px rgba(98,114,245,0.15)",
              }}
            >
              <div className="flex-1 flex items-center gap-3 px-4">
                <span className="text-lg">🔗</span>
                <input
                  type="url"
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={DEMO_URL_HINT}
                  className="flex-1 bg-transparent text-sm outline-none py-3"
                  style={{ color: "var(--text-primary)", fontFamily: "'DM Sans', sans-serif" }}
                />
                {url && (
                  <button onClick={() => setUrl("")}
                    className="text-lg transition-opacity hover:opacity-70"
                    style={{ color: "var(--text-muted)" }}>
                    ×
                  </button>
                )}
              </div>

              <button
                onClick={handleSubmit}
                disabled={!url.trim()}
                className="px-6 py-3 rounded-xl text-sm font-semibold transition-all hover:scale-105 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  background: "linear-gradient(135deg,#6272f5,#8b5cf6)",
                  color: "white",
                  boxShadow: "0 0 20px rgba(98,114,245,0.4)",
                }}
              >
                Analyze →
              </button>
            </div>

            {/* Error */}
            {status === "error" && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-3 text-center text-sm"
                style={{ color: "#ef4444" }}
              >
                ⚠️ {error || "Analysis failed. Please try again."}
              </motion.p>
            )}

            {/* Example links */}
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>Try example:</span>
              {EXAMPLE_URLS.map((u, i) => (
                <button key={i} onClick={() => setUrl(u)}
                  className="text-xs underline decoration-dotted transition-colors hover:text-blue-400"
                  style={{ color: "var(--text-muted)" }}>
                  Example {i + 1}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── Loading ───────────────────────────────────────────── */}
        <AnimatePresence>
          {status === "loading" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="max-w-md mx-auto py-8"
            >
              <LoadingSteps steps={steps} currentStep={currentStep} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Results ──────────────────────────────────────────── */}
        <AnimatePresence>
          {status === "success" && result && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* New analysis button */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    Analysis complete in {result.processing_time_ms}ms
                  </span>
                </div>
                <button
                  onClick={handleReset}
                  className="text-sm px-4 py-2 rounded-xl transition-all hover:scale-105"
                  style={{
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    color: "var(--text-secondary)",
                  }}
                >
                  ← New Analysis
                </button>
              </div>

              {/* Two-column layout */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left: Tweet Card */}
                <div>
                  <h2 className="font-display font-bold text-xl mb-4"
                    style={{ color: "var(--text-primary)" }}>
                    Tweet
                  </h2>
                  <TweetCard
                    tweetData={result.tweet_data}
                    sentiment={result.sentiment}
                  />
                </div>

                {/* Right: Dashboard */}
                <div>
                  <SentimentDashboard result={result} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Feature cards (shown on idle) ─────────────────────── */}
        {status === "idle" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4 max-w-4xl mx-auto"
          >
            {[
              { icon: "🧠", title: "RoBERTa NLP", desc: "Twitter-fine-tuned transformer" },
              { icon: "🖼️", title: "ViT Vision",  desc: "Image sentiment via patches" },
              { icon: "😊", title: "Emoji AI",    desc: "3000+ emoji lexicon scores" },
              { icon: "⚡", title: "Fusion Layer", desc: "Weighted multimodal merge" },
            ].map(({ icon, title, desc }) => (
              <div key={title} className="rounded-xl p-4 text-center"
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.07)",
                }}>
                <div className="text-2xl mb-2">{icon}</div>
                <div className="text-sm font-semibold mb-1" style={{ color: "var(--text-primary)" }}>{title}</div>
                <div className="text-xs" style={{ color: "var(--text-muted)" }}>{desc}</div>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
