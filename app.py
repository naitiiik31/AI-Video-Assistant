import streamlit as st
import time
import json
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant | Meeting Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (Glassmorphism & Animations) ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-color: #0f172a;
    --glass-bg: rgba(30, 41, 59, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    --primary: #8b5cf6;
    --primary-hover: #7c3aed;
    --secondary: #06b6d4;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --success: #10b981;
    --warning: #f59e0b;
}

/* Global Reset */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg-color) !important;
    color: var(--text-main) !important;
}

.stApp {
    background: radial-gradient(circle at top left, #1e1b4b, #0f172a 40%, #020617 100%) !important;
}

/* Animated Background Elements */
.stApp::before, .stApp::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    z-index: -1;
    animation: float 20s infinite ease-in-out alternate;
}
.stApp::before {
    top: -10%; left: -10%;
    width: 50vw; height: 50vw;
    background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
}
.stApp::after {
    bottom: -10%; right: -10%;
    width: 60vw; height: 60vw;
    background: radial-gradient(circle, rgba(6,182,212,0.1) 0%, transparent 70%);
    animation-delay: -10s;
}

@keyframes float {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(5%, 5%) scale(1.1); }
}

/* Sidebar Glassmorphism */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid var(--glass-border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}

/* Typography */
h1, h2, h3, h4 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text-main) !important;
}

/* Hero Section */
.hero-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 4rem 0 3rem 0;
    animation: fadeIn 1s ease-out;
    width: 100%;
}
.hero-title {
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 50%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: var(--text-muted) !important;
    max-width: 650px;
    margin: 0 auto;
    font-weight: 300;
    line-height: 1.6;
    text-align: center !important;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Glass Cards */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
    border-color: rgba(139, 92, 246, 0.4);
}

.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--secondary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    gap: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    height: 3.5rem;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 8px 8px 0 0;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 1.05rem;
    padding: 0 1rem;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 3px solid var(--primary);
    background: rgba(139, 92, 246, 0.05);
}

/* Input & Buttons */
.stTextInput input {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: white !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s ease;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: white !important;
    transition: all 0.3s ease;
}
.stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, #6d28d9 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.39) !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid var(--glass-border) !important;
    box-shadow: none !important;
    color: var(--text-main) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: var(--text-muted) !important;
}

/* Status Indicator */
.status-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1rem;
    border-radius: 10px;
    background: rgba(255,255,255,0.03);
    margin-bottom: 0.5rem;
    border: 1px solid transparent;
    transition: all 0.3s ease;
}
.status-active {
    border-color: rgba(139,92,246,0.4);
    background: rgba(139,92,246,0.15);
    transform: translateX(5px);
}
.pulse-dot {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}
.dot-active { background: var(--secondary); box-shadow: 0 0 12px var(--secondary); animation: pulse 1.5s infinite; }
.dot-done { background: var(--success); box-shadow: 0 0 8px var(--success); }
.dot-pending { background: var(--text-muted); opacity: 0.3; }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
}

/* Chat Bubbles */
.chat-wrapper {
    background: var(--glass-bg);
    border-radius: 16px;
    border: 1px solid var(--glass-border);
    padding: 1.5rem;
    height: 450px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    scroll-behavior: smooth;
}
.chat-bubble {
    padding: 1rem 1.2rem;
    border-radius: 16px;
    max-width: 85%;
    line-height: 1.6;
    font-size: 0.95rem;
    animation: fadeIn 0.3s ease-out;
}
.bubble-user {
    background: linear-gradient(135deg, var(--primary), #6d28d9);
    align-self: flex-end;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 15px rgba(139,92,246,0.2);
}
.bubble-ai {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--glass-border);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
    color: var(--text-main);
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }

/* Download buttons wrapper */
.download-btn-container .stDownloadButton button {
    width: 100%;
    background: rgba(6, 182, 212, 0.1) !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    color: var(--secondary) !important;
}
.download-btn-container .stDownloadButton button:hover {
    background: rgba(6, 182, 212, 0.2) !important;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
if "result" not in st.session_state: st.session_state.result = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "pipeline_done" not in st.session_state: st.session_state.pipeline_done = False
if "pipeline_steps" not in st.session_state: st.session_state.pipeline_steps = {}

# ─── Helpers ────────────────────────────────────────────────────────────────────
def render_step(label, key, icon):
    state = st.session_state.pipeline_steps.get(key, "pending")
    dot_class = f"dot-{state}"
    active_class = "status-active" if state == "active" else ""
    color_style = "color: var(--text-main);" if state != "pending" else "color: var(--text-muted);"
    st.markdown(f"""
    <div class="status-item {active_class}">
        <div class="pulse-dot {dot_class}"></div>
        <span style="font-size:1.2rem">{icon}</span>
        <span style="font-weight:500; font-size:0.95rem; {color_style}">{label}</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding-bottom: 2rem; padding-top: 1rem;">
        <div style="font-size: 3.5rem; margin-bottom: -10px; animation: float 6s ease-in-out infinite;">✨</div>
        <h2 style="background: linear-gradient(90deg, #c4b5fd, #8b5cf6, #67e8f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; margin-bottom: 0;">AI Video</h2>
        <p style="color: var(--secondary); font-size: 0.85rem; letter-spacing: 3px; text-transform: uppercase; font-weight: 600; margin-top: 5px;">Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem;'>⚙️ Configuration</h4>", unsafe_allow_html=True)
    source = st.text_input("Media Source", placeholder="YouTube URL or local path...")
    language = st.selectbox("Transcription Language", ["english", "hinglish"], help="Select the primary language of the video.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Analyze Video", use_container_width=True)
    
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'>", unsafe_allow_html=True)
    
    # Progress Section
    st.markdown("<h4 style='color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem;'>🔄 Processing Pipeline</h4>", unsafe_allow_html=True)
    render_step("Audio Extraction", "audio", "🔊")
    render_step("Transcription", "transcript", "📝")
    render_step("Semantic Title", "title", "🏷️")
    render_step("Smart Summary", "summary", "📋")
    render_step("Data Extraction", "extract", "🔍")
    render_step("RAG Engine Init", "rag", "🧠")
    
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05)'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.8rem; color: var(--text-muted); text-align: center; background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
        <p style="margin-bottom: 5px; font-weight: 600; color: var(--text-main);">Built for Job Interview Demo</p>
        <p style="font-size: 0.75rem; margin-bottom: 0;">Powered by LLMs & Advanced RAG</p>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Area ──────────────────────────────────────────────────────────────────
if not st.session_state.pipeline_done and not st.session_state.result:
    # Beautiful Empty State
    st.markdown("""
    <div class="hero-wrapper">
        <h1 class="hero-title">Transform Meetings into<br>Actionable Intelligence</h1>
        <div class="hero-subtitle">Upload a video or paste a YouTube link to instantly generate semantic summaries, extract key decisions, and chat interactively with your meeting content.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    features = [
        ("⚡", "Lightning Fast", "Process long videos in minutes with highly optimized AI pipelines and async operations."),
        ("🧠", "Smart Extraction", "Automatically identify action items, strategic decisions, and critical open questions."),
        ("💬", "Interactive Q&A", "Chat naturally with your video transcript using state-of-default RAG technology.")
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(139,92,246,0.3));">{icon}</div>
                <h3 style="font-size: 1.3rem; margin-bottom: 0.8rem; color: #f8fafc;">{title}</h3>
                <p style="color: var(--text-muted); font-size: 0.95rem; line-height: 1.6;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("⚠️ Please enter a YouTube URL or file path to begin.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_container = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_container.container():
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 4rem 2rem; margin-top: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem; animation: pulse 2s infinite;">⚙️</div>
                    <h2 style="color: var(--secondary); margin-bottom: 1rem;">Processing Video Intelligence</h2>
                    <p style="color: var(--text-muted); font-size: 1.1rem;">Our AI is currently analyzing your content. Check the sidebar for live pipeline status...</p>
                </div>
                """, unsafe_allow_html=True)

            update_step("audio", "active"); st.rerun() if False else None
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_container.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_container.error(f"❌ Processing Error: {e}")

# ── Results Dashboard ───────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    
    # Header Section
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem; padding-top: 1rem;">
        <span style="background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3); color: #c4b5fd; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">Intelligence Report</span>
        <h1 style="font-size: clamp(2rem, 4vw, 3rem); margin-top: 1rem; line-height: 1.2; background: linear-gradient(to right, #fff, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{r['title']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Export Options
    report_data = f"# {r['title']}\n\n## Summary\n{r['summary']}\n\n## Action Items\n{r['action_items']}\n\n## Key Decisions\n{r['key_decisions']}\n\n## Open Questions\n{r['open_questions']}"
    
    st.markdown('<div class="download-btn-container">', unsafe_allow_html=True)
    col_dl1, col_dl2, col_dl3, col_spacer = st.columns([2.2, 2.2, 2.2, 5.4])
    
    with col_dl1:
        st.download_button("📥 Report (MD)", report_data, file_name="meeting_report.md", mime="text/markdown", use_container_width=True)
        
    with col_dl2:
        try:
            from fpdf import FPDF
            class PDF(FPDF):
                def header(self):
                    self.set_font('Arial', 'B', 15)
                    self.cell(0, 10, 'Meeting Intelligence Report', 0, 1, 'C')
                    self.ln(5)
                def footer(self):
                    self.set_y(-15)
                    self.set_font('Arial', 'I', 8)
                    self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
            pdf = PDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            def clean_text(text):
                if not text: return ""
                text = str(text).replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
                text = text.replace('\u2013', '-').replace('\u2014', '--').replace('\u2022', '*')
                return text.encode('latin-1', 'replace').decode('latin-1')
            def add_section(heading, text):
                pdf.set_font('Arial', 'B', 12)
                pdf.set_text_color(139, 92, 246)
                pdf.cell(0, 10, clean_text(heading), 0, 1, 'L')
                pdf.set_font('Arial', '', 10)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(0, 6, clean_text(text))
                pdf.ln(5)
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 10, clean_text(r['title']), align='C')
            pdf.ln(10)
            add_section("Executive Summary", r['summary'])
            add_section("Action Items", r['action_items'])
            add_section("Key Decisions", r['key_decisions'])
            add_section("Open Questions", r['open_questions'])
            try:
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
            except AttributeError:
                pdf_bytes = bytes(pdf.output())
            
            st.download_button("📥 Report (PDF)", pdf_bytes, file_name="meeting_report.pdf", mime="application/pdf", use_container_width=True)
        except ImportError:
            st.download_button("📥 Report (PDF)", "Please install 'fpdf' (pip install fpdf) to enable PDF downloads.", file_name="install_fpdf.txt", mime="text/plain", use_container_width=True, help="Requires 'fpdf' package")
            
    with col_dl3:
        st.download_button("📥 Transcript (TXT)", r['transcript'], file_name="transcript.txt", mime="text/plain", use_container_width=True)
        
    st.markdown('</div><br>', unsafe_allow_html=True)

    # Interactive Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Executive Summary", "🎯 Key Insights", "📝 Full Transcript", "💬 AI Q&A Chat"])
    
    with tab1:
        st.markdown(f"""
        <div class="glass-card" style="font-size: 1.1rem; line-height: 1.8; color: #e2e8f0; padding: 2rem;">
            {r['summary'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
    with tab2:
        ic1, ic2, ic3 = st.columns(3)
        with ic1:
            st.markdown(f"""
            <div class="glass-card" style="height: 100%;">
                <div class="card-title">
                    <span style="font-size: 1.2rem;">✅</span> Action Items
                </div>
                <div style="color: #cbd5e1; font-size: 1rem; line-height: 1.7;">{r['action_items'].replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
        with ic2:
            st.markdown(f"""
            <div class="glass-card" style="height: 100%;">
                <div class="card-title">
                    <span style="font-size: 1.2rem;">🔑</span> Key Decisions
                </div>
                <div style="color: #cbd5e1; font-size: 1rem; line-height: 1.7;">{r['key_decisions'].replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
        with ic3:
            st.markdown(f"""
            <div class="glass-card" style="height: 100%;">
                <div class="card-title">
                    <span style="font-size: 1.2rem;">❓</span> Open Questions
                </div>
                <div style="color: #cbd5e1; font-size: 1rem; line-height: 1.7;">{r['open_questions'].replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
    with tab3:
        st.markdown(f"""
        <div class="glass-card" style="max-height: 600px; overflow-y: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; line-height: 1.8; color: #94a3b8; padding: 2rem;">
            {r['transcript'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
    with tab4:
        col_chat, col_info = st.columns([2.5, 1])
        
        with col_chat:
            # Chat Display
            chat_html = '<div class="chat-wrapper" id="chat-container">'
            if not st.session_state.chat_history:
                chat_html += """
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-muted); opacity: 0.8;">
                    <div style="font-size: 4rem; margin-bottom: 1rem; filter: grayscale(100%); opacity: 0.5;">🤖</div>
                    <h3 style="color: var(--text-main); margin-bottom: 0.5rem;">Ask the AI Assistant</h3>
                    <p style="text-align: center; max-width: 80%;">I have analyzed the entire transcript. Ask me anything about the meeting!</p>
                    <div style="margin-top: 1rem; padding: 0.5rem 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 0.85rem; border: 1px dashed rgba(255,255,255,0.1);">
                        e.g., "What was the main deadline?" or "Summarize the technical architecture."
                    </div>
                </div>
                """
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    chat_html += f'<div class="chat-bubble bubble-user">{msg["content"]}</div>'
                else:
                    chat_html += f'<div class="chat-bubble bubble-ai"><div style="font-weight: 700; color: var(--secondary); margin-bottom: 0.3rem; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">AI Assistant</div>{msg["content"]}</div>'
            chat_html += '</div>'
            
            # Autoscroll script trick for Streamlit components
            chat_html += """
            <script>
                var chatContainer = document.getElementById('chat-container');
                if(chatContainer){
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            </script>
            """
            st.markdown(chat_html, unsafe_allow_html=True)
            
            # Chat Input Form
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("chat_form", clear_on_submit=True):
                c1, c2 = st.columns([5, 1])
                with c1:
                    user_input = st.text_input("Message", placeholder="Type your question here...", label_visibility="collapsed")
                with c2:
                    submitted = st.form_submit_button("Send ✨", use_container_width=True)
                    
            if submitted and user_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
                with st.spinner("Analyzing context..."):
                    answer = ask_question(r["rag_chain"], user_input.strip())
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

        with col_info:
            st.markdown("""
            <div class="glass-card" style="position: sticky; top: 1rem;">
                <h4 style="color: var(--secondary); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">🧠</span> RAG Engine
                </h4>
                <p style="color: var(--text-main); font-size: 0.9rem; margin-bottom: 1rem;">Retrieval-Augmented Generation capabilities:</p>
                <ul style="color: var(--text-muted); font-size: 0.9rem; padding-left: 1rem; line-height: 1.7; margin-bottom: 1.5rem;">
                    <li>Answers grounded strictly in the meeting transcript.</li>
                    <li>Context-aware semantic search.</li>
                    <li>Zero-hallucination guarantee based on provided context.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.chat_history:
                if st.button("🗑️ Clear Conversation", type="secondary", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
