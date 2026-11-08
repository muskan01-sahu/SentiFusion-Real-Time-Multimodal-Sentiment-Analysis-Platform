import jsPDF from "jspdf";

export const exportToPDF = async (result) => {
  const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
  const margin = 20;
  const pageW = 210;
  let y = margin;

  const addLine = (text, size = 11, bold = false, color = [30, 30, 50]) => {
    doc.setFontSize(size);
    doc.setFont("helvetica", bold ? "bold" : "normal");
    doc.setTextColor(...color);
    doc.text(text, margin, y);
    y += size * 0.5 + 3;
  };

  const addDivider = () => {
    doc.setDrawColor(200, 200, 230);
    doc.setLineWidth(0.3);
    doc.line(margin, y, pageW - margin, y);
    y += 6;
  };

  // Header
  doc.setFillColor(62, 72, 245);
  doc.rect(0, 0, pageW, 35, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(255, 255, 255);
  doc.text("SentimentAI — Analysis Report", margin, 16);
  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.text(`Generated: ${new Date().toLocaleString()}`, margin, 26);
  y = 50;

  // Tweet Info
  addLine("TWEET INFORMATION", 13, true, [62, 72, 245]);
  addDivider();
  if (result.tweet_data) {
    addLine(`Author: ${result.tweet_data.author} (${result.tweet_data.author_handle})`, 10);
    addLine(`Tweet: ${result.tweet_data.text?.substring(0, 200) || "N/A"}`, 10);
    addLine(`Timestamp: ${result.tweet_data.timestamp || "N/A"}`, 10);
    addLine(`Engagement: ❤️ ${result.tweet_data.likes || 0}  🔁 ${result.tweet_data.retweets || 0}  💬 ${result.tweet_data.replies_count || 0}`, 10);
    y += 5;
  }

  // Sentiment Result
  addLine("SENTIMENT ANALYSIS RESULT", 13, true, [62, 72, 245]);
  addDivider();
  if (result.sentiment) {
    const sentiment = result.sentiment.final?.toUpperCase() || "N/A";
    const confidence = ((result.sentiment.confidence || 0) * 100).toFixed(1);
    addLine(`Final Sentiment: ${sentiment}`, 14, true);
    addLine(`Confidence Score: ${confidence}%`, 11);
    y += 3;

    // Breakdown
    addLine("Modality Breakdown:", 11, true);
    const bd = result.sentiment.breakdown || {};
    if (bd.text) addLine(`  • Text (RoBERTa):  ${bd.text.label?.toUpperCase()} — ${(bd.text.score * 100).toFixed(1)}%`, 10);
    if (bd.emoji) addLine(`  • Emoji (Lexicon): ${bd.emoji.label?.toUpperCase()} — ${(bd.emoji.score * 100).toFixed(1)}%`, 10);
    if (bd.image) addLine(`  • Image (ViT):     ${bd.image.label?.toUpperCase()} — ${(bd.image.score * 100).toFixed(1)}%`, 10);
    y += 5;
  }

  // Model Comparison
  addLine("MODEL COMPARISON", 13, true, [62, 72, 245]);
  addDivider();
  if (result.model_comparison) {
    Object.entries(result.model_comparison).forEach(([model, score]) => {
      addLine(`  ${model.toUpperCase()}: ${(score * 100).toFixed(1)}%`, 10);
    });
    y += 5;
  }

  // Sarcasm
  addLine("SARCASM DETECTION", 13, true, [62, 72, 245]);
  addDivider();
  if (result.sarcasm) {
    addLine(`Sarcasm Detected: ${result.sarcasm.detected ? "YES ⚠️" : "NO ✅"}`, 10);
    addLine(`Sarcasm Probability: ${(result.sarcasm.score * 100).toFixed(1)}%`, 10);
    y += 5;
  }

  // Footer
  doc.setFontSize(8);
  doc.setTextColor(150, 150, 170);
  doc.text(
    "SentimentAI — Real-Time Multimodal Sentiment Analysis | Final Year B.Tech Project",
    pageW / 2,
    290,
    { align: "center" }
  );

  doc.save(`SentimentAI_Report_${Date.now()}.pdf`);
};
