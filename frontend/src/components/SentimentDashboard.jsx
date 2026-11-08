import { motion } from "framer-motion";
import ConfidenceMeter from "./Charts/ConfidenceMeter";
import SentimentPieChart from "./Charts/SentimentPieChart";
import ModelComparisonBar from "./Charts/ModelComparisonBar";
import EmojiVisualizer from "./EmojiVisualizer";
import ModalityBreakdown from "./ModalityBreakdown";
import { exportToPDF } from "../utils/pdfExport";

const LANG_LABELS = {
  en: "🇺🇸 English",
  hi: "🇮🇳 Hindi / Hinglish",
  es: "🇪🇸 Spanish",
  fr: "🇫🇷 French",
};

function SarcasmBadge({ sarcasm }) {
  if (!sarcasm) return null;
  return (
    <div className="rounded-2xl p-5"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <h3 className="text-xs font-semibold uppercase tracking-widest mb-3"
        style={{ color: "var(--text-muted)" }}>
        Sarcasm Detection
      </h3>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{sarcasm.detected ? "⚠️" : "✅"}</span>
        <div>
          <div className="text-sm font-semibold" style={{ color: sarcasm.detected ? "#f59e0b" : "#10b981" }}>
            {sarcasm.detected ? "Sarcasm Detected" : "No Sarcasm Detected"}
          </div>
          <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
            Probability: {(sarcasm.score * 100).toFixed(1)}%
          </div>
        </div>
        {/* Sarcasm score bar */}
        <div className="flex-1 ml-2">
          <div className="rounded-full h-1.5 overflow-hidden"
            style={{ background: "rgba(255,255,255,0.06)" }}>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${sarcasm.score * 100}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="h-full rounded-full"
              style={{ background: sarcasm.detected ? "#f59e0b" : "#10b981" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function MetaInfo({ language, processingTime, analysisId }) {
  return (
    <div className="rounded-2xl p-4 flex flex-wrap gap-4"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border-subtle)" }}>
      <div>
        <div className="text-xs" style={{ color: "var(--text-muted)" }}>Language</div>
        <div className="text-sm font-medium mt-0.5" style={{ color: "var(--text-primary)" }}>
          {LANG_LABELS[language] || language?.toUpperCase() || "Unknown"}
        </div>
      </div>
      <div>
        <div className="text-xs" style={{ color: "var(--text-muted)" }}>Processing Time</div>
        <div className="text-sm font-medium font-mono mt-0.5" style={{ color: "#6272f5" }}>
          {processingTime ? `${processingTime}ms` : "—"}
        </div>
      </div>
      <div>
        <div className="text-xs" style={{ color: "var(--text-muted)" }}>Analysis ID</div>
        <div className="text-xs font-mono mt-0.5 truncate max-w-[140px]"
          style={{ color: "var(--text-muted)" }}>
          {analysisId?.slice(0, 12) || "—"}
        </div>
      </div>
    </div>
  );
}

export default function SentimentDashboard({ result }) {
  if (!result) return null;

  const { sentiment, tweet_data, model_comparison, sarcasm, language,
          fusion_weights, processing_time_ms, analysis_id } = result;

  const handleExportPDF = () => exportToPDF(result);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="space-y-4"
    >
      {/* Dashboard header */}
      <div className="flex items-center justify-between">
        <h2 className="font-display font-bold text-xl" style={{ color: "var(--text-primary)" }}>
          Analysis Results
        </h2>
        <button
          onClick={handleExportPDF}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all hover:scale-105 active:scale-95"
          style={{
            background: "rgba(98,114,245,0.15)",
            border: "1px solid rgba(98,114,245,0.35)",
            color: "#6272f5",
          }}
        >
          📄 Export PDF
        </button>
      </div>

      {/* Confidence Meter — full width */}
      <ConfidenceMeter
        sentiment={sentiment?.final}
        confidence={sentiment?.confidence}
      />

      {/* Charts row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <SentimentPieChart scores={sentiment?.breakdown?.text?.scores} />
        <ModelComparisonBar modelComparison={model_comparison} />
      </div>

      {/* Modality breakdown */}
      <ModalityBreakdown
        breakdown={sentiment?.breakdown}
        fusionWeights={fusion_weights}
      />

      {/* Emoji visualizer */}
      <EmojiVisualizer
        emojiScores={sentiment?.breakdown?.emoji?.emoji_scores}
        emojisFound={sentiment?.breakdown?.emoji?.emojis_found}
      />

      {/* Sarcasm */}
      <SarcasmBadge sarcasm={sarcasm} />

      {/* Meta info */}
      <MetaInfo
        language={language}
        processingTime={processing_time_ms}
        analysisId={analysis_id}
      />
    </motion.div>
  );
}
