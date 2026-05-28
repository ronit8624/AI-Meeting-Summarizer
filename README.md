# 🎙️ AI Meeting Summarizer

An intelligent meeting summarization platform that automatically transcribes audio, identifies speakers, generates summaries, extracts action items, and enables chat with your meeting transcript using RAG.

---

## ✨ Features

- 🎤 **Speech-to-Text** — faster-whisper (CTranslate2, INT8 quantized) — 4x faster than vanilla Whisper
- 🎙️ **Speaker Diarization** — pyannote.audio 3.1 — identifies *who* spoke and *when*
- 🔤 **Word-level Alignment** — WhisperX — precise timestamps merged with speaker labels
- 📋 **AI Summarization** — Mistral API — generates meeting title, bullet-point summary, key decisions
- ✅ **Action Item Extraction** — Pydantic structured output — task, owner, deadline, priority
- 💬 **RAG Chat** — ChromaDB + LangChain — chat with your meeting transcript
- 🌐 **Streamlit UI** — dark theme, live pipeline status, diarization toggle

---

## 🏗️ Architecture

```
Audio Input (YouTube URL / Local File)
        ↓
Audio Download & Chunking (yt-dlp + pydub)
        ↓
Speech-to-Text (faster-whisper)
        ↓
Word Alignment (WhisperX)
        ↓
Speaker Diarization (pyannote.audio)
        ↓
Diarized Transcript → [SPEAKER_00]: Hello everyone...
        ↓
Mistral API (LangChain)
    ├── Title Generation
    ├── Summary (bullet points)
    ├── Action Items (Pydantic structured)
    ├── Key Decisions
    └── Open Questions
        ↓
ChromaDB Vector Store → RAG Chat
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Speech-to-Text | faster-whisper 1.1.0 (CTranslate2 INT8) |
| Speaker Diarization | pyannote.audio 3.1.1 |
| Word Alignment | WhisperX 3.1.1 |
| LLM | Mistral API (mistral-small-latest) |
| LLM Orchestration | LangChain |
| Vector Store | ChromaDB |
| UI | Streamlit |
| Package Manager | uv |

---

## ⚙️ Prerequisites

- Python 3.11
- [uv](https://docs.astral.sh/uv/) package manager
- [Mistral API Key](https://console.mistral.ai/)
- [Hugging Face Account + Token](https://huggingface.co/settings/tokens) (Read type)
- ffmpeg installed on system

### Install ffmpeg (Mac)
```bash
brew install ffmpeg
```

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/AI-Meeting-Summarizer.git
cd AI-Meeting-Summarizer
```

### 2. Install uv (if not already installed)
```bash
pip install uv
```

### 3. Install all dependencies
```bash
uv sync
```
This uses `uv.lock` to install exact pinned versions — no dependency conflicts.

### 4. Accept Hugging Face model licenses
You must accept the license for these models (one-time):
- [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
- [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
- [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)

Click **"Agree and access repository"** on each page while logged into your HF account.

### 5. Create `.env` file
```bash
cp .env.example .env
```
Fill in your keys:
```
MISTRAL_API_KEY=your_mistral_api_key_here
HF_TOKEN=hf_your_huggingface_token_here
```

### 6. Run the app
```bash
source .venv/bin/activate
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📖 Usage

1. Paste a **YouTube URL** or enter a **local audio/video file path** in the sidebar
2. Select the **language** (English / Hinglish)
3. Toggle **Speaker Diarization** on/off
4. Click **⚡ Analyse**
5. Wait for the pipeline to complete (first run downloads models)
6. View **Summary**, **Action Items**, **Key Decisions**, **Open Questions**
7. Chat with your meeting using the **RAG Chat** at the bottom

---

## 📁 Project Structure

```
AI-Meeting-Summarizer/
├── app.py                  # Streamlit UI — main entry point
├── main.py                 # CLI entry point
├── pyproject.toml          # Project dependencies (uv)
├── uv.lock                 # Locked dependency versions
├── Requirements.txt        # pip fallback requirements
├── .env.example            # Environment variables template
├── core/
│   ├── transcriber.py      # faster-whisper speech-to-text
│   ├── aligner.py          # WhisperX alignment + diarization merge
│   ├── diarizer.py         # pyannote speaker diarization
│   ├── summarizer.py       # Mistral summarization via LangChain
│   ├── extractor.py        # Action item extraction (Pydantic)
│   ├── rag_engine.py       # RAG chat pipeline
│   └── vector_store.py     # ChromaDB vector store
└── utils/
    └── audio_processor.py  # Audio download, conversion, chunking
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `MISTRAL_API_KEY` | Mistral API key from [console.mistral.ai](https://console.mistral.ai/) |
| `HF_TOKEN` | Hugging Face Read token from [hf.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `WHISPER_MODEL` | Whisper model size: `tiny`, `small`, `medium`, `large-v3` (default: `small`) |
| `WHISPER_DEVICE` | `cpu` or `cuda` (default: `cpu`) |

---

## ⚠️ Notes

- First run will download AI models (~500MB) — subsequent runs use cache
- Processing time depends on audio length and CPU speed
- Speaker diarization requires HF token and model license acceptance
- Tested on Apple Silicon (M-series) Mac with Python 3.11

---

## 📄 License

MIT License
