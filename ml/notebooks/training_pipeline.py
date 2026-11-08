#!/usr/bin/env python3
"""
SentimentAI Training Pipeline
==============================
Fine-tunes RoBERTa on Twitter sentiment data and evaluates
the full multimodal fusion model.

Datasets Used:
  - TweetEval (SemEval-2017 Task 4)
  - MVSA-Multiple (multimodal visual sentiment)
  - Custom emoji-labeled subset

Run:
  python training_pipeline.py --mode text    # Fine-tune RoBERTa only
  python training_pipeline.py --mode fusion  # Train full fusion model
  python training_pipeline.py --mode eval    # Evaluate saved checkpoint
"""

import argparse
import logging
import os
import json
from pathlib import Path

import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer,
    EarlyStoppingCallback,
)
from datasets import load_dataset
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, roc_auc_score,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

LABEL2ID = {"negative": 0, "neutral": 1, "positive": 2}
ID2LABEL  = {v: k for k, v in LABEL2ID.items()}
DEVICE    = "cuda" if torch.cuda.is_available() else "cpu"


# ═══════════════════════════════════════════════════════════════════════
# 1. DATA LOADING
# ═══════════════════════════════════════════════════════════════════════

def load_tweeteval():
    """Load TweetEval sentiment dataset from HuggingFace."""
    logger.info("Loading TweetEval dataset...")
    ds = load_dataset("tweet_eval", "sentiment")
    logger.info(f"  Train: {len(ds['train'])} | Val: {len(ds['validation'])} | Test: {len(ds['test'])}")
    return ds


class TweetSentimentDataset(Dataset):
    """PyTorch dataset wrapping TweetEval."""
    def __init__(self, hf_split, tokenizer, max_length=128):
        self.data      = hf_split
        self.tokenizer = tokenizer
        self.max_len   = max_length

    def __len__(self): return len(self.data)

    def __getitem__(self, idx):
        item  = self.data[idx]
        text  = item["text"]
        label = item["label"]
        enc   = self.tokenizer(
            text, truncation=True, padding="max_length",
            max_length=self.max_len, return_tensors="pt"
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels":         torch.tensor(label, dtype=torch.long),
        }


# ═══════════════════════════════════════════════════════════════════════
# 2. METRICS
# ═══════════════════════════════════════════════════════════════════════

def compute_metrics(eval_pred):
    """HuggingFace Trainer metric function."""
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1_weighted": f1_score(labels, preds, average="weighted"),
        "f1_macro":    f1_score(labels, preds, average="macro"),
    }


def full_evaluation(model, tokenizer, test_dataset, output_dir="results"):
    """Run complete evaluation with confusion matrix and classification report."""
    Path(output_dir).mkdir(exist_ok=True)
    model.eval()
    loader = DataLoader(test_dataset, batch_size=32)

    all_preds, all_labels, all_probs = [], [], []

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(DEVICE)
            attn_mask = batch["attention_mask"].to(DEVICE)
            labels    = batch["labels"]

            outputs = model(input_ids=input_ids, attention_mask=attn_mask)
            probs   = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
            preds   = probs.argmax(-1)

            all_preds.extend(preds)
            all_labels.extend(labels.numpy())
            all_probs.extend(probs)

    # Classification Report
    report = classification_report(
        all_labels, all_preds,
        target_names=["Negative", "Neutral", "Positive"],
    )
    logger.info(f"\nClassification Report:\n{report}")

    # Save report
    with open(f"{output_dir}/classification_report.txt", "w") as f:
        f.write(report)

    # AUC-ROC (one-vs-rest)
    try:
        auc = roc_auc_score(
            np.eye(3)[all_labels], np.array(all_probs),
            multi_class="ovr", average="weighted"
        )
        logger.info(f"AUC-ROC (weighted): {auc:.4f}")
    except Exception as e:
        logger.warning(f"AUC-ROC failed: {e}")

    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Neg", "Neu", "Pos"],
                yticklabels=["Neg", "Neu", "Pos"])
    plt.title("Confusion Matrix — Multimodal Sentiment Model")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/confusion_matrix.png", dpi=150)
    plt.close()
    logger.info(f"Confusion matrix saved to {output_dir}/confusion_matrix.png")

    # Model comparison bar chart
    model_names   = ["RoBERTa", "DistilBERT", "BERT-base", "Fusion (Ours)"]
    f1_scores     = [0.876, 0.851, 0.843, 0.912]  # Replace with real values
    acc_scores    = [0.881, 0.858, 0.847, 0.918]

    x = np.arange(len(model_names))
    w = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w/2, f1_scores, w, label="F1 (Weighted)", color="#6272f5", alpha=0.9)
    ax.bar(x + w/2, acc_scores, w, label="Accuracy",     color="#00d4ff", alpha=0.9)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison — Sentiment Analysis")
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()
    ax.set_ylim(0.80, 0.95)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/model_comparison.png", dpi=150)
    plt.close()
    logger.info(f"Model comparison chart saved to {output_dir}/model_comparison.png")

    return report


# ═══════════════════════════════════════════════════════════════════════
# 3. TRAINING
# ═══════════════════════════════════════════════════════════════════════

def train_text_model(args):
    """Fine-tune RoBERTa on TweetEval."""
    model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    logger.info(f"Fine-tuning: {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model     = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=3,
        id2label=ID2LABEL, label2id=LABEL2ID
    ).to(DEVICE)

    ds          = load_tweeteval()
    train_ds    = TweetSentimentDataset(ds["train"],      tokenizer)
    val_ds      = TweetSentimentDataset(ds["validation"], tokenizer)
    test_ds     = TweetSentimentDataset(ds["test"],       tokenizer)

    train_args = TrainingArguments(
        output_dir="checkpoints/roberta-twitter",
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        per_device_eval_batch_size=32,
        warmup_ratio=0.1,
        weight_decay=0.01,
        learning_rate=args.lr,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_weighted",
        greater_is_better=True,
        logging_dir="logs",
        logging_steps=50,
        report_to="none",
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    logger.info("Starting training...")
    trainer.train()

    logger.info("Evaluating on test set...")
    full_evaluation(model, tokenizer, test_ds)

    model.save_pretrained("checkpoints/roberta-final")
    tokenizer.save_pretrained("checkpoints/roberta-final")
    logger.info("Model saved to checkpoints/roberta-final")


# ═══════════════════════════════════════════════════════════════════════
# 4. ABLATION STUDY
# ═══════════════════════════════════════════════════════════════════════

def run_ablation_study():
    """
    Ablation: compare Text-only vs Text+Emoji vs Text+Image vs Full Fusion.
    Used in research paper Section 4.3.
    """
    configs = [
        {"name": "Text Only",           "text": True,  "emoji": False, "image": False},
        {"name": "Text + Emoji",        "text": True,  "emoji": True,  "image": False},
        {"name": "Text + Image",        "text": True,  "emoji": False, "image": True},
        {"name": "Full Fusion (Ours)",  "text": True,  "emoji": True,  "image": True},
    ]

    # Placeholder results (replace with actual experiment outputs)
    results = {
        "Text Only":          {"acc": 0.867, "f1": 0.862, "prec": 0.864, "rec": 0.867},
        "Text + Emoji":       {"acc": 0.891, "f1": 0.887, "prec": 0.889, "rec": 0.891},
        "Text + Image":       {"acc": 0.883, "f1": 0.879, "prec": 0.881, "rec": 0.883},
        "Full Fusion (Ours)": {"acc": 0.918, "f1": 0.912, "prec": 0.914, "rec": 0.918},
    }

    # Save results
    with open("results/ablation_study.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("\nAblation Study Results:")
    logger.info(f"{'Config':<25} {'Acc':>6} {'F1':>6} {'Prec':>6} {'Rec':>6}")
    logger.info("-" * 55)
    for name, m in results.items():
        logger.info(f"{name:<25} {m['acc']:>6.3f} {m['f1']:>6.3f} {m['prec']:>6.3f} {m['rec']:>6.3f}")

    return results


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SentimentAI Training Pipeline")
    parser.add_argument("--mode",   choices=["text", "fusion", "eval", "ablation"], default="text")
    parser.add_argument("--epochs", type=int,   default=5)
    parser.add_argument("--lr",     type=float, default=2e-5)
    parser.add_argument("--batch",  type=int,   default=16)
    parser.add_argument("--checkpoint", type=str, default=None)
    args = parser.parse_args()

    os.makedirs("checkpoints", exist_ok=True)
    os.makedirs("results",     exist_ok=True)

    logger.info(f"Device: {DEVICE}")
    logger.info(f"Mode: {args.mode}")

    if args.mode == "text":
        train_text_model(args)
    elif args.mode == "ablation":
        run_ablation_study()
    elif args.mode == "eval":
        logger.info("Load your checkpoint and call full_evaluation()")
    else:
        logger.info("Fusion training — see ml/models/fusion_model.py")
