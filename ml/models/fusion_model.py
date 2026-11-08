"""
Multimodal Fusion Model — PyTorch Implementation
For research, fine-tuning, and training pipeline.

Architecture:
  TextEncoder  (RoBERTa → 768-dim CLS embedding)
  ImageEncoder (ViT     → 768-dim CLS embedding)
  EmojiEncoder (MLP on emoji2vec → 256-dim)
  FusionMLP    (Concat 1792-dim → Dense → 3-class)

Usage:
  python fusion_model.py --train
  python fusion_model.py --eval --checkpoint checkpoints/best.pt
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    RobertaModel, RobertaTokenizer,
    ViTModel, ViTFeatureExtractor,
)
from torch.utils.data import Dataset, DataLoader
import numpy as np
import logging

logger = logging.getLogger(__name__)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 3  # positive, negative, neutral
LABEL2ID = {"positive": 2, "neutral": 1, "negative": 0}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}

# ─── Text Encoder ─────────────────────────────────────────────────────────────

class TextEncoder(nn.Module):
    """RoBERTa encoder producing a 768-dim text representation."""
    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment-latest", freeze_base=False):
        super().__init__()
        self.roberta = RobertaModel.from_pretrained(model_name)
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
        self.proj = nn.Sequential(
            nn.Linear(768, 768),
            nn.LayerNorm(768),
            nn.GELU(),
            nn.Dropout(0.1),
        )
        if freeze_base:
            for param in self.roberta.parameters():
                param.requires_grad = False

    def forward(self, input_ids, attention_mask):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # [B, 768]
        return self.proj(cls_embedding)

    def encode_text(self, texts: list[str], max_length=128) -> dict:
        return self.tokenizer(
            texts, padding=True, truncation=True,
            max_length=max_length, return_tensors="pt"
        )


# ─── Image Encoder ────────────────────────────────────────────────────────────

class ImageEncoder(nn.Module):
    """ViT encoder producing a 768-dim image representation."""
    def __init__(self, model_name="google/vit-base-patch16-224", freeze_base=False):
        super().__init__()
        self.vit = ViTModel.from_pretrained(model_name)
        self.proj = nn.Sequential(
            nn.Linear(768, 768),
            nn.LayerNorm(768),
            nn.GELU(),
            nn.Dropout(0.1),
        )
        if freeze_base:
            for param in self.vit.parameters():
                param.requires_grad = False

    def forward(self, pixel_values):
        outputs = self.vit(pixel_values=pixel_values)
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # [B, 768]
        return self.proj(cls_embedding)


# ─── Emoji Encoder ────────────────────────────────────────────────────────────

class EmojiEncoder(nn.Module):
    """Projects emoji sentiment features to a fixed-size embedding."""
    def __init__(self, input_dim=64, hidden_dim=256, output_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, output_dim),
            nn.LayerNorm(output_dim),
        )

    def forward(self, emoji_features):
        return self.net(emoji_features)


# ─── Fusion Model ─────────────────────────────────────────────────────────────

class MultimodalSentimentFusion(nn.Module):
    """
    Full multimodal fusion model.

    Input:
      text_ids, text_mask   — tokenized tweet text
      pixel_values          — processed image (or zeros if no image)
      emoji_features        — emoji feature vector
      has_image             — boolean mask indicating valid image inputs

    Output:
      logits [B, 3]         — raw logits for softmax
      embeddings dict       — intermediate representations
    """
    def __init__(
        self,
        text_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest",
        image_model: str = "google/vit-base-patch16-224",
        emoji_input_dim: int = 64,
        freeze_text: bool = True,
        freeze_image: bool = True,
    ):
        super().__init__()
        self.text_encoder  = TextEncoder(text_model, freeze_base=freeze_text)
        self.image_encoder = ImageEncoder(image_model, freeze_base=freeze_image)
        self.emoji_encoder = EmojiEncoder(input_dim=emoji_input_dim)

        # Learnable modality weights
        self.text_weight  = nn.Parameter(torch.tensor(0.55))
        self.image_weight = nn.Parameter(torch.tensor(0.20))
        self.emoji_weight = nn.Parameter(torch.tensor(0.25))

        # Fusion MLP
        fusion_input_dim = 768 + 768 + 256  # text + image + emoji = 1792
        self.fusion = nn.Sequential(
            nn.Linear(fusion_input_dim, 1024),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Linear(256, NUM_CLASSES),
        )

        # Cross-modal attention
        self.cross_attn = nn.MultiheadAttention(embed_dim=768, num_heads=8, batch_first=True)

    def forward(self, text_ids, text_mask, pixel_values, emoji_features, has_image=None):
        # Encode each modality
        text_emb  = self.text_encoder(text_ids, text_mask)      # [B, 768]
        image_emb = self.image_encoder(pixel_values)             # [B, 768]
        emoji_emb = self.emoji_encoder(emoji_features)           # [B, 256]

        # Mask out image embeddings where no image exists
        if has_image is not None:
            mask = has_image.float().unsqueeze(-1)  # [B, 1]
            image_emb = image_emb * mask

        # Cross-modal attention: text attends to image
        text_seq   = text_emb.unsqueeze(1)   # [B, 1, 768]
        image_seq  = image_emb.unsqueeze(1)  # [B, 1, 768]
        attended, _ = self.cross_attn(text_seq, image_seq, image_seq)
        text_enriched = attended.squeeze(1) + text_emb  # residual

        # Weighted combination before fusion
        w_text  = torch.sigmoid(self.text_weight)
        w_img   = torch.sigmoid(self.image_weight)
        w_emoji = torch.sigmoid(self.emoji_weight)

        # Concatenate
        fused = torch.cat([
            text_enriched * w_text,
            image_emb     * w_img,
            emoji_emb     * w_emoji,
        ], dim=-1)  # [B, 1792]

        logits = self.fusion(fused)

        return logits, {
            "text_emb":  text_emb,
            "image_emb": image_emb,
            "emoji_emb": emoji_emb,
            "fused":     fused,
        }


# ─── Training Utils ───────────────────────────────────────────────────────────

class FocalLoss(nn.Module):
    """Focal loss for handling class imbalance."""
    def __init__(self, gamma=2.0, alpha=None):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha

    def forward(self, inputs, targets):
        ce = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce)
        focal = (1 - pt) ** self.gamma * ce
        return focal.mean()


def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch in loader:
        optimizer.zero_grad()

        text_ids      = batch["text_ids"].to(device)
        text_mask     = batch["text_mask"].to(device)
        pixel_values  = batch["pixel_values"].to(device)
        emoji_feats   = batch["emoji_features"].to(device)
        has_image     = batch["has_image"].to(device)
        labels        = batch["labels"].to(device)

        logits, _ = model(text_ids, text_mask, pixel_values, emoji_feats, has_image)
        loss = criterion(logits, labels)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        total_loss += loss.item()
        preds = logits.argmax(-1)
        correct += (preds == labels).sum().item()
        total += len(labels)

    return total_loss / len(loader), correct / total


@torch.no_grad()
def eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    all_preds, all_labels = [], []

    for batch in loader:
        text_ids      = batch["text_ids"].to(device)
        text_mask     = batch["text_mask"].to(device)
        pixel_values  = batch["pixel_values"].to(device)
        emoji_feats   = batch["emoji_features"].to(device)
        has_image     = batch["has_image"].to(device)
        labels        = batch["labels"].to(device)

        logits, _ = model(text_ids, text_mask, pixel_values, emoji_feats, has_image)
        loss = criterion(logits, labels)

        total_loss += loss.item()
        all_preds.extend(logits.argmax(-1).cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    from sklearn.metrics import f1_score, classification_report
    f1 = f1_score(all_labels, all_preds, average="weighted")
    report = classification_report(all_labels, all_preds, target_names=list(LABEL2ID.keys()))

    return total_loss / len(loader), f1, report


def main_train():
    """Main training entry point."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",   type=int,   default=10)
    parser.add_argument("--lr",       type=float, default=2e-5)
    parser.add_argument("--batch",    type=int,   default=16)
    parser.add_argument("--checkpoint", type=str, default="checkpoints/best.pt")
    args = parser.parse_args()

    logger.info(f"Training on: {DEVICE}")

    model = MultimodalSentimentFusion(
        freeze_text=True,
        freeze_image=True,
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    criterion = FocalLoss(gamma=2.0)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # TODO: Replace with real DataLoader from your dataset
    # train_loader = DataLoader(TweetSentimentDataset("data/train.csv"), batch_size=args.batch, shuffle=True)
    # val_loader   = DataLoader(TweetSentimentDataset("data/val.csv"),   batch_size=args.batch)

    logger.info("Model architecture summary:")
    total_params = sum(p.numel() for p in model.parameters())
    trainable    = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"  Total params:     {total_params:,}")
    logger.info(f"  Trainable params: {trainable:,}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main_train()
