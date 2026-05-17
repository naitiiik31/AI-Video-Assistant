# 🎬 AI Video Assistant

> **Transcribe · Summarise · Chat with your meetings**

An AI-powered meeting intelligence tool that takes any YouTube video or local video/audio file and turns it into structured insights — transcripts, summaries, action items, key decisions, and an interactive RAG-powered chat interface.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Whisper](https://img.shields.io/badge/OpenAI_Whisper-ASR-412991?style=for-the-badge&logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![MistralAI](https://img.shields.io/badge/Mistral_AI-LLM-FF7000?style=for-the-badge)](https://mistral.ai)
[![LangChain](https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=for-the-badge)](https://langchain.com)

</div>

---

## 🚀 Live Demo

<div align="center">

### **[🔗 Launch App →](https://www.google.com)**

*Try it live — no setup required*

</div>

---

## 📸 Screenshots

<br>

### 🏠 Homepage — Dashboard Overview

![Homepage](assets/screenshots/homepage.png)

<br>

### 📝 Transcript & Summary Panel

![Transcript](assets/screenshots/transcript.png)

<br>

### 💬 RAG Chat Interface

![Chat](assets/screenshots/chat.png)

<br>

### 🎬 Full Demo

![Demo](assets/demo.gif)

---

## ✨ Features

- **🔊 Audio Processing** — Supports YouTube URLs and local video/audio files via `yt-dlp` and `pydub`
- **📝 Transcription** — Accurate speech-to-text using OpenAI Whisper (supports English & Hinglish)
- **🏷️ Auto Title Generation** — Automatically generates a descriptive session title from the transcript
- **📋 Summarisation** — Concise meeting summary powered by Mistral AI via LangChain
- **🔍 Smart Extraction** — Extracts action items, key decisions, and open questions from the transcript
- **🧠 RAG Chat** — Ask anything about your meeting using a Retrieval-Augmented Generation chain (ChromaDB + Sentence Transformers + MistralAI)
- **🎨 Custom UI** — Sleek dark-themed Streamlit interface with live pipeline status tracking

---

## 🗂️ Project Structure

```
AI-Video-Assistant/
├── app.py                  # Main Streamlit application & UI
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── core/
│   ├── transcriber.py      # Whisper-based transcription
│   ├── summarizer.py       # LLM summarisation & title generation
│   ├── extractor.py        # Action items / decisions / questions extraction
│   └── rag_engine.py       # RAG chain builder & question answering
├── utils/
│   └── audio_processor.py  # YouTube download & audio chunking
└── vector_db/              # ChromaDB persistent vector store
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- `ffmpeg` installed and available on your system PATH
- A [Mistral AI API key](https://console.mistral.ai/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/naitiiik31/AI-Video-Assistant.git
cd AI-Video-Assistant

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

### Run the App

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🛠️ How It Works

1. **Input** — Paste a YouTube URL or a local file path into the sidebar
2. **Audio Processing** — The video is downloaded and chunked into audio segments
3. **Transcription** — Whisper transcribes the audio to text
4. **Analysis** — The transcript is passed through LLM pipelines to generate a title, summary, action items, key decisions, and open questions
5. **RAG Indexing** — The transcript is embedded and stored in ChromaDB for semantic search
6. **Chat** — Ask natural language questions about the meeting and get grounded answers

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Transcription | OpenAI Whisper |
| LLM | Mistral AI |
| Orchestration | LangChain |
| Vector Store | ChromaDB |
| Embeddings | Sentence Transformers (HuggingFace) |
| Audio | yt-dlp, pydub, ffmpeg |
| Translation | deep-translator |

---

## 📦 Key Dependencies

```
openai-whisper        # Speech-to-text transcription
langchain             # LLM orchestration framework
langchain-mistralai   # Mistral AI integration
chromadb              # Vector database for RAG
sentence-transformers # Text embeddings
yt-dlp                # YouTube audio download
streamlit             # Web UI framework
pydub                 # Audio processing
```

---

## 🌐 Supported Languages

- **English**
- **Hinglish** (Hindi-English code-mixed speech)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. See the repository for license details.

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/naitiiik31">naitiiik31</a>
</div>
