import { motion, AnimatePresence } from "framer-motion";

export default function LoadingSteps({ steps, currentStep }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-md mx-auto"
    >
      {/* Spinner */}
      <div className="flex justify-center mb-8">
        <div className="relative w-20 h-20">
          <div className="absolute inset-0 rounded-full border-2 border-transparent"
            style={{ borderTopColor: "#6272f5", animation: "spin 1s linear infinite" }} />
          <div className="absolute inset-2 rounded-full border-2 border-transparent"
            style={{ borderTopColor: "#00d4ff", animation: "spin 1.5s linear infinite reverse" }} />
          <div className="absolute inset-4 rounded-full border-2 border-transparent"
            style={{ borderTopColor: "#8b5cf6", animation: "spin 2s linear infinite" }} />
          <div className="absolute inset-0 flex items-center justify-center text-2xl">
            {steps[currentStep]?.icon || "⚡"}
          </div>
        </div>
      </div>

      {/* Steps List */}
      <div className="space-y-3">
        {steps.map((step, idx) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.08 }}
            className="flex items-center gap-3 px-4 py-3 rounded-xl"
            style={{
              background: idx === currentStep
                ? "rgba(98,114,245,0.12)"
                : step.done
                ? "rgba(16,185,129,0.08)"
                : "rgba(255,255,255,0.03)",
              border: `1px solid ${
                idx === currentStep
                  ? "rgba(98,114,245,0.35)"
                  : step.done
                  ? "rgba(16,185,129,0.25)"
                  : "rgba(255,255,255,0.05)"
              }`,
              transition: "all 0.3s ease",
            }}
          >
            {/* Status Icon */}
            <div className="w-7 h-7 rounded-full flex items-center justify-center text-sm flex-shrink-0"
              style={{
                background: step.done
                  ? "rgba(16,185,129,0.2)"
                  : idx === currentStep
                  ? "rgba(98,114,245,0.2)"
                  : "rgba(255,255,255,0.05)",
              }}
            >
              {step.done ? "✓" : idx === currentStep ? (
                <span style={{ animation: "pulse 1s infinite" }}>•</span>
              ) : "○"}
            </div>

            {/* Label */}
            <span className="text-sm font-medium flex-1"
              style={{
                color: step.done
                  ? "#10b981"
                  : idx === currentStep
                  ? "#f0f0ff"
                  : "var(--text-muted)",
              }}
            >
              {step.label}
            </span>

            {/* Spinner for current */}
            {idx === currentStep && !step.done && (
              <div className="w-4 h-4 rounded-full border-2 border-transparent flex-shrink-0"
                style={{
                  borderTopColor: "#6272f5",
                  animation: "spin 0.8s linear infinite",
                }} />
            )}

            {/* Check for done */}
            {step.done && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-emerald-400 flex-shrink-0"
              >
                ✓
              </motion.span>
            )}
          </motion.div>
        ))}
      </div>

      <p className="text-center text-xs mt-6" style={{ color: "var(--text-muted)" }}>
        Running deep learning models — this may take a few seconds
      </p>
    </motion.div>
  );
}
