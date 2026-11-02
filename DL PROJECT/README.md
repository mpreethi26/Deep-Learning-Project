# Premium AI-Powered Abstractive Text Summarization Application

## Academic NLP Deep Learning Project
- **Team Lead**: **CHOUDAM BHARATH REDDY**
- **Application Area**: Text Summarization
- **Overall Domain**: Natural Language Processing (NLP)
- **Research Keywords**: `abstractive text summarization transformer`
- **Required Research Publisher**: **IEEE Xplore**
- **Primary Model**: `sshleifer/distilbart-cnn-12-6` (DistilBART)
- **Comparative Model**: `Falconsai/text_summarization` (T5-small Fine-Tuned for Summarization)
- **Frontend Framework**: React 18 with Vite, TypeScript, Tailwind CSS, Lucide React, Recharts
- **Backend Framework**: Python FastAPI, Uvicorn, Pydantic
- **Deep Learning Framework**: PyTorch & Hugging Face Transformers

---

## 📖 Project Overview
This project delivers a complete, end-to-end, production-grade Natural Language Processing application for genuine **abstractive text summarization**. Unlike traditional extractive systems that merely clip and concatenate existing sentences, this application utilizes pretrained sequence-to-sequence Transformer models to generate novel, fluent, and coherent natural-language summaries.

The application features:
1. **Interactive Text Workspace:** Paste long-form articles, reports, and papers with live word, character, and token metrics.
2. **PDF Document Summarization:** Automated PyMuPDF text extraction across multi-page documents with OCR-requirement detection.
3. **Length-Calibrated Abstractive Generation:** 4 verified presets (Short 80–120w, Medium 150–250w, Long 300–500w, Detailed 500–800w) with length penalty calibration and sentence completion trimming.
4. **Hierarchical Long-Document Chunking:** Sliding window segmentation with paragraph and sentence preservation to summarize long documents exceeding model token ceilings without destructive over-compression.
5. **Transformer Model Comparison:** Side-by-side DistilBART (`sshleifer/distilbart-cnn-12-6`) vs T5-small (`Falconsai/text_summarization`) inference on the same source text with latency and compression analytics.
6. **Summary Evaluation Dashboard:** Reference-based ROUGE evaluation (ROUGE-1, ROUGE-2, ROUGE-L) with interactive Recharts bar charts and mathematical interpretations.
7. **Session History:** Thread-safe persistent history storage (`data/history.json`), search filters, copy, download (TXT/MD), and record deletion.
8. **Research & IEEE Methodology:** Formal documentation aligning with IEEE Xplore literature, transformer self-attention equations, BART denoising autoencoder mechanics, and architectural schematics.

All core functionality executes locally on Windows without requiring paid external cloud API keys.

---

## 🔍 Root Cause Diagnosis: Why Summaries Were Previously Too Short

### 1. Underlying Causes Identified:
- **News Corpus Inductive Bias:** `facebook/bart-large-cnn` was fine-tuned on CNN/DailyMail where reference highlights average 3–4 sentences (50–80 tokens). Autoregressive beam search naturally emitted the EOS token `</s>` after ~60 tokens.
- **Premature Beam Cutoff:** `early_stopping=True` with low token budgets halted generation as soon as beams completed.
- **Conflation of Words and Tokens:** 1 English word $\approx$ 1.35 tokens. Old configurations had `max_tokens: 140` (producing at most ~90 words) and lacked a `detailed` preset entirely.
- **Destructive Hierarchical Compression:** The legacy pipeline compressed intermediate chunks down to `max_tokens // len(chunks)` (~40 tokens), then compressed that concatenation again, squashing a multi-page document into a mere 60 words.

### 2. Solutions Implemented in This Application:
- **Calibrated Token Budgets & Length Penalties:** Calibrated `min_new_tokens`, `max_new_tokens`, and length penalties ($1.2 \to 2.5$) across Short, Medium, Long, and Detailed profiles.
- **Section-Wise Hierarchical Synthesis:** For multi-chunk documents, chunk summaries receive substantial budgets (110–220 tokens) and are formatted as structured multi-paragraph syntheses (`Executive Overview` + `Detailed Section Syntheses`).
- **Grounded Bounds & Sentence Trimming:** Automatically clamps generation budgets when input is brief to prevent hallucinations, and cleanly trims dangling trailing fragments to complete sentence boundaries.

---

## 🏗️ System Architecture
```
Input Document (Pasted Text or Multi-Page PDF)
        │
        ▼
PyMuPDF Text Extraction & Sanitization
        │
        ▼
Tokenization & Sliding-Window Chunking (BPE)
        │
        ▼
Transformer Bidirectional Encoder
        │
        ▼
Cross-Attention Autoregressive Decoder (Beam Search)
        │
        ▼
Length-Aware Bounded Refinement & Sentence Trimming
        │
        ▼
FastAPI REST API ──► React + Vite UI (Tailwind CSS, Recharts)
        │
        ▼
ROUGE Evaluation & Multi-Format Export (TXT / MD)
```

---

## 💻 Tech Stack

### Frontend
- **React 18** with **Vite**
- **TypeScript**
- **Tailwind CSS** (v4)
- **Lucide React** (icons)
- **Recharts** (evaluation metrics visualizations)
- **Axios** (API communication)

### Backend
- **Python 3.11 / 3.12 / 3.13**
- **FastAPI** & **Uvicorn**
- **Pydantic** (data validation)
- **Hugging Face Transformers**
- **PyTorch** (`torch.inference_mode()`)
- **PyMuPDF** (`pymupdf`)
- **ROUGE** (`rouge-score`)
- **Pandas** & **NumPy**
- **Pytest**

---

## 🚀 Setup & Execution Guide (Windows & VS Code)

### 1. Prerequisites
- Windows 10 or 11
- Python 3.11+ installed and added to PATH
- Node.js 18+ and npm installed

### 2. Backend Setup
Open a terminal in the root project directory:
```powershell
# Create & activate virtual environment (optional if global Python has requirements)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI backend server with Uvicorn
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI backend runs at: `http://127.0.0.1:8000`  
Interactive Swagger API documentation: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
Open a second terminal in the `frontend/` directory:
```powershell
cd frontend
npm install
npm run dev
```
The React frontend runs at: `http://localhost:5173`

---

## 🧪 Running Automated Tests
Run the comprehensive test suite (25 unit and integration tests):
```powershell
pytest -v
```

---

## 📊 Dataset Benchmark Experiment
To execute benchmark experiments on dataset samples and export to CSV:
```powershell
python experiments/evaluate_dataset.py --model bart --output experiment_results.csv
```

---

## 📚 IEEE Xplore Base Paper Documentation
- **Paper**: *Abstractive Text Summarization using Deep Learning Transformers and Sequence-to-Sequence Modeling*
- **Publisher**: **IEEE Xplore** (Conference: SIST)
- **DOI**: [10.1109/SIST50301.2021.9465942](https://doi.org/10.1109/SIST50301.2021.9465942)
- **Search Query**: `abstractive text summarization transformer`
- Documented in: [`research/ieee_base_paper_template.md`](file:///c:/Users/Bharath94911/OneDrive/Desktop/DL%20PROJECT/research/ieee_base_paper_template.md) and [`research/methodology.md`](file:///c:/Users/Bharath94911/OneDrive/Desktop/DL%20PROJECT/research/methodology.md).

---

## 👨‍💻 Project Lead
**CHOUDAM BHARATH REDDY**  
Department of Computer Science & Engineering / AI & Data Science  
Domain: Deep Learning & Natural Language Processing

