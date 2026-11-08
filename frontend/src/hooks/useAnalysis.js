import { useState, useCallback } from "react";
import { analyzeTweet } from "../utils/api";

const STEPS = [
  { id: "fetch",   label: "Fetching tweet data...",        icon: "🔗" },
  { id: "text",    label: "Analyzing text with RoBERTa...", icon: "🧠" },
  { id: "emoji",   label: "Processing emoji sentiment...", icon: "😊" },
  { id: "image",   label: "Running ViT image model...",    icon: "🖼️" },
  { id: "fusion",  label: "Fusing multimodal signals...",  icon: "⚡" },
  { id: "done",    label: "Analysis complete!",            icon: "✅" },
];

const STEP_DELAYS = [800, 1400, 900, 1200, 700, 400];

export function useAnalysis() {
  const [status, setStatus]           = useState("idle"); // idle | loading | success | error
  const [result, setResult]           = useState(null);
  const [error, setError]             = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps]             = useState(STEPS.map(s => ({ ...s, done: false })));

  const simulateSteps = useCallback(async (analyzePromise) => {
    for (let i = 0; i < STEPS.length - 1; i++) {
      setCurrentStep(i);
      await new Promise(r => setTimeout(r, STEP_DELAYS[i]));
      setSteps(prev => prev.map((s, idx) => idx <= i ? { ...s, done: true } : s));
    }
    // Wait for actual result
    const data = await analyzePromise;
    setCurrentStep(STEPS.length - 1);
    setSteps(prev => prev.map(s => ({ ...s, done: true })));
    await new Promise(r => setTimeout(r, 400));
    return data;
  }, []);

  const analyze = useCallback(async (url) => {
    setStatus("loading");
    setError(null);
    setResult(null);
    setCurrentStep(0);
    setSteps(STEPS.map(s => ({ ...s, done: false })));

    const promise = analyzeTweet(url);
    try {
      const data = await simulateSteps(promise);
      setResult(data);
      setStatus("success");
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Analysis failed");
      setStatus("error");
    }
  }, [simulateSteps]);

  const reset = useCallback(() => {
    setStatus("idle");
    setResult(null);
    setError(null);
    setCurrentStep(0);
    setSteps(STEPS.map(s => ({ ...s, done: false })));
  }, []);

  return { status, result, error, currentStep, steps, analyze, reset };
}
