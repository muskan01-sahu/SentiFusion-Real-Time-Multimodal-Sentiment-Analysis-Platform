# 🧠 Real-Time Multimodal Sentiment Analysis of Social Media Tweets

> **Final Year B.Tech Project** | Deep Learning + Transformer Models + Multimodal Fusion

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)](https://fastapi.tiangolo.com)
[![HuggingFace](https://img.shields.io/badge/🤗-Transformers-FF6B6B)](https://huggingface.co)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📌 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Model Architecture](#model-architecture)
- [Deployment Guide](#deployment-guide)
- [Research Paper Notes](#research-paper-notes)

---

## 🎯 Project Overview

A production-grade web application that performs **multimodal sentiment analysis** on tweets by combining:
- **Text Analysis** via RoBERTa (fine-tuned on Twitter data)
- **Emoji Sentiment** via emoji2vec embeddings + lexicon scoring
- **Image Analysis** via Vision Transformer (ViT-base)
- **Fusion Layer** combining all modalities into a final prediction

### Key Features
| Feature | Status |
|---|---|
| Tweet URL Processing | ✅ |
| BERT/RoBERTa Text Sentiment | ✅ |
| Emoji-Aware Scoring | ✅ |
| ViT Image Sentiment | ✅ |
| Multimodal Fusion | ✅ |
| Dashboard with Charts | ✅ |
| Sarcasm Detection | ✅ |
| Hinglish Support | ✅ |
| PDF Report Export | ✅ |
| Analysis History | ✅ |
| Real-Time Loading Steps | ✅ |
| Dark/Light Mode | ✅ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  Tweet URL Input → Tweet Card → Dashboard → Charts → PDF Export │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (FastAPI)
┌──────────────────────────▼──────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  /analyze → Tweet Scraper → Preprocessing → Model Pipeline      │
└──────────┬──────────────────┬───────────────────────────────────┘
           │                  │
┌──────────▼──────┐  ┌────────▼────────────────────────────────┐
│  Tweet Scraper  │  │         ML Pipeline                      │
│  (tweepy/snscrape)│  │  ┌──────────┐ ┌──────────┐ ┌────────┐│
└─────────────────┘  │  │ RoBERTa  │ │ Emoji2Vec│ │  ViT   ││
                     │  │ (Text)   │ │ (Emoji)  │ │ (Image)││
                     │  └────┬─────┘ └────┬─────┘ └───┬────┘│
                     │       └────────────┴────────────┘     │
                     │            Fusion Layer (MLP)          │
                     │         Final Sentiment Output         │
                     └────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Tool | Purpose |
|---|---|
| React 18 + Vite | UI Framework |
| Tailwind CSS | Styling |
| Framer Motion | Animations |
| Recharts | Data Visualization |
| Axios | API Calls |
| jsPDF + html2canvas | PDF Export |
| React Router | Navigation |

### Backend
| Tool | Purpose |
|---|---|
| FastAPI | REST API |
| Uvicorn | ASGI Server |
| Tweepy / snscrape | Tweet Fetching |
| SQLite + SQLAlchemy | Analysis History |
| Pydantic | Data Validation |

### ML/NLP
| Tool | Purpose |
|---|---|
| HuggingFace Transformers | BERT, RoBERTa, ViT |
| PyTorch | Model Inference |
| emoji | Emoji Processing |
| emoji2vec | Emoji Embeddings |
| langdetect | Language Detection |
| Pillow | Image Processing |
| NLTK | Text Preprocessing |

---

## 📁 Folder Structure

```
sentiment-app/
├── frontend/                    # React Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── TweetCard.jsx        # Tweet display component
│   │   │   ├── SentimentDashboard.jsx
│   │   │   ├── LoadingSteps.jsx     # Real-time loading UI
│   │   │   ├── Charts/
│   │   │   │   ├── PieChart.jsx
│   │   │   │   ├── BarChart.jsx
│   │   │   │   └── ConfidenceMeter.jsx
│   │   │   ├── EmojiVisualizer.jsx
│   │   │   ├── HistoryPanel.jsx
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Analysis.jsx
│   │   │   └── History.jsx
│   │   ├── hooks/
│   │   │   ├── useAnalysis.js
│   │   │   └── useTheme.js
│   │   ├── utils/
│   │   │   ├── api.js
│   │   │   └── pdfExport.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── backend/                     # FastAPI Application
│   ├── main.py                  # App entry point
│   ├── routes/
│   │   ├── analyze.py           # /analyze endpoint
│   │   └── history.py           # /history endpoint
│   ├── models/
│   │   └── database.py          # SQLAlchemy models
│   ├── services/
│   │   ├── tweet_scraper.py     # Tweet fetching
│   │   ├── text_analyzer.py     # RoBERTa pipeline
│   │   ├── emoji_analyzer.py    # Emoji sentiment
│   │   ├── image_analyzer.py    # ViT pipeline
│   │   └── fusion.py            # Multimodal fusion
│   ├── utils/
│   │   └── preprocessor.py      # Text cleaning
│   └── requirements.txt
│
├── ml/                          # ML Model Code
│   ├── models/
│   │   ├── roberta_sentiment.py
│   │   ├── vit_image.py
│   │   ├── emoji_model.py
│   │   └── fusion_model.py
│   ├── notebooks/
│   │   └── training_notebook.ipynb
│   └── data/
│       └── emoji_sentiment_lexicon.json
│
├── docker-compose.yml
├── Dockerfile.frontend
├── Dockerfile.backend
└── README.md
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.10+
- pip
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sentiment-app.git
cd sentiment-app
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
py -3.10 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Set environment variables
cp .env.example .env
# Edit .env with your Twitter API keys (optional - scraper works without it)

# Start backend server
python -m uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔌 API Documentation

### POST `/analyze`
Analyze a tweet URL for sentiment.

**Request:**
```json
{
  "tweet_url": "https://twitter.com/user/status/123456789",
  "include_replies": false
}
```

**Response:**
```json
{
  "tweet_data": {
    "text": "Tweet text here 😊",
    "author": "@username",
    "timestamp": "2024-01-15T10:30:00Z",
    "images": ["https://..."],
    "emojis": ["😊", "🔥"]
  },
  "sentiment": {
    "final": "positive",
    "confidence": 0.87,
    "label": "Positive",
    "breakdown": {
      "text": { "label": "positive", "score": 0.91 },
      "emoji": { "label": "positive", "score": 0.85 },
      "image": { "label": "positive", "score": 0.79 }
    }
  },
  "model_comparison": {
    "roberta": 0.91,
    "distilbert": 0.88,
    "bert": 0.86
  },
  "sarcasm": {
    "detected": false,
    "score": 0.12
  },
  "language": "en",
  "analysis_id": "uuid-here"
}
```

### GET `/history`
Get past analysis results.

### GET `/history/{id}`
Get a specific analysis result.

---

## 🧠 Model Architecture

### Text Model: cardiffnlp/twitter-roberta-base-sentiment-latest
- Pre-trained on 124M tweets
- Fine-tuned for 3-class sentiment (Positive/Negative/Neutral)
- Output: logits → softmax → confidence scores

### Emoji Model: Custom Emoji Sentiment Scorer
- emoji2vec embeddings (300-dim)
- Sentiment lexicon with 3000+ emoji mappings
- Weighted average across all emojis in text

### Image Model: google/vit-base-patch16-224
- Vision Transformer pre-trained on ImageNet-21k
- Fine-tuned on sentiment-labeled image datasets
- Output: patch embeddings → CLS token → sentiment class

### Fusion Model: Weighted MLP
```
text_features (768) + emoji_features (300) + image_features (768)
     → Concatenate (1836) → Dense(512, ReLU) → Dropout(0.3)
     → Dense(256, ReLU) → Dense(3, Softmax)
     → Weighted sum with modal confidence weights
```

---

## 🚀 Deployment Guide

### Docker (Recommended)
```bash
# Build and run all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Vercel (Frontend)
```bash
cd frontend
npm run build
vercel deploy --prod
```

### Render (Backend)
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Environment Variables
```env
# Backend .env
TWITTER_BEARER_TOKEN=your_token_here   # Optional
DATABASE_URL=sqlite:///./sentiment.db
MODEL_CACHE_DIR=./model_cache
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

---

## 📝 Research Paper Notes

### Novel Contributions
1. **Emoji-Aware Multimodal Fusion**: Novel weighted fusion of text, emoji, and image modalities
2. **Hinglish Support**: Code-mixed Hindi-English sentiment detection
3. **Sarcasm-Aware Scoring**: Adjusts confidence based on sarcasm probability
4. **Real-Time Processing Pipeline**: Sub-3-second full multimodal inference

### Datasets Referenced
- SemEval-2017 Task 4 (Twitter Sentiment)
- TweetEval Benchmark
- MVSA-Multiple (Multimodal Visual Sentiment Analysis)
- Emoji Sentiment Ranking Dataset

### Evaluation Metrics
- Accuracy, F1-Score (Macro + Weighted)
- Per-class Precision/Recall
- AUC-ROC
- Cohen's Kappa

---

## 📄 License

MIT License © 2024 — Final Year B.Tech Project
