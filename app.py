import streamlit as st
import time
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all

try:
    from core.aligner import diarize_audio
except Exception:
    diarize_audio = None

from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

:root{
    --bg:#050510;
    --surface:#0f0f1a;
    --surface2:#181825;
    --border:#2a2a3a;
    --accent:#7c3aed;
    --accent2:#06b6d4;
    --text:#f5f5ff;
    --muted:#8b8ba7;
}

html, body, [class*="css"]{
    font-family:'Inter', sans-serif;
    background:var(--bg);
    color:var(--text);
}

.stApp{
    background:var(--bg);
}

[data-testid="stSidebar"]{
    background:var(--surface);
    border-right:1px solid var(--border);
}

.hero-title{
    font-family:'Syne', sans-serif;
    font-size:4rem;
    font-weight:800;

    background:linear-gradient(
        135deg,
        #ffffff 0%,
        #8b5cf6 50%,
        #06b6d4 100%
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    margin-bottom:0.3rem;
}

.hero-sub{
    color:var(--muted);
    letter-spacing:0.2rem;
    text-transform:uppercase;
    font-size:0.8rem;
    margin-bottom:2rem;
}

.card{
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:18px;
    padding:1.5rem;
    margin-bottom:1rem;
}

.card-title{
    color:var(--muted);
    font-size:0.8rem;
    text-transform:uppercase;
    letter-spacing:0.15rem;
    margin-bottom:1rem;
    font-weight:700;
}

.stButton>button{
    width:100%;
    background:linear-gradient(
        135deg,
        #7c3aed,
        #5b21b6
    ) !important;

    color:white !important;
    border:none !important;
    border-radius:12px !important;
    font-weight:700 !important;
    padding:0.8rem !important;
}

.chat-user{
    background:rgba(124,58,237,0.15);
    border-radius:12px;
    padding:1rem;
    margin-bottom:0.8rem;
}

.chat-bot{
    background:rgba(6,182,212,0.10);
    border-radius:12px;
    padding:1rem;
    margin-bottom:1rem;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    st.markdown("""
    <div class="hero-title" style="font-size:2.2rem;">
        🎙️ AI Meeting
    </div>

    <div class="hero-sub">
        Summarizer
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/... or local audio file"
    )

    enable_diarization = st.checkbox(
        "Enable Speaker Diarization",
        value=False,
        help="Slower but identifies speakers"
    )

    st.markdown("---")

    run_btn = st.button("⚡ Analyse")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-title">
    AI Meeting Summarizer
</div>

<div class="hero-sub">
    Transcribe · Summarise · Chat
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# RUN PIPELINE
# ─────────────────────────────────────────────
if run_btn:

    if not source.strip():

        st.error("Please enter a valid YouTube URL or audio file.")

    else:

        try:

            progress = st.progress(0)

            with st.spinner("🔊 Processing audio..."):

                chunks = process_input(source)

                progress.progress(20)

            with st.spinner("📝 Transcribing audio..."):

                if enable_diarization and diarize_audio is not None:

                    diarized_chunks = []

                    for chunk_path in chunks:

                        diarized = diarize_audio(
                            chunk_path,
                            None
                        )

                        if diarized is None:

                            fallback = transcribe_all(
                                [chunk_path],
                                None
                            )

                            diarized_chunks.append(fallback)

                        else:

                            diarized_chunks.append(diarized)

                    transcript = "\n".join(diarized_chunks)

                else:

                    transcript = transcribe_all(
                        chunks,
                        None
                    )

                progress.progress(55)

            with st.spinner("📌 Generating title..."):

                title = generate_title(transcript)

                progress.progress(70)

            with st.spinner("📋 Generating summary..."):

                summary = summarize(transcript)

                progress.progress(80)

            with st.spinner("🧠 Extracting insights..."):

                action_items = extract_action_items(transcript)

                decisions = extract_key_decisions(transcript)

                questions = extract_questions(transcript)

                progress.progress(90)

            with st.spinner("🔍 Building RAG engine..."):

                rag_chain = build_rag_chain(transcript)

                progress.progress(100)

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }

            st.success("✅ Analysis Complete")

            time.sleep(1)

            st.rerun()

        except Exception as e:

            st.error(f"❌ Error: {e}")

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
if st.session_state.result:

    r = st.session_state.result

    st.markdown("## 📌 Generated Title")
    st.subheader(r["title"])

    col1, col2 = st.columns([3, 2])

    with col1:

        st.markdown("## 📋 Summary")

        st.write(r["summary"])

    with col2:

        st.markdown("## 📝 Transcript")

        st.text_area(
            label="Transcript",
            value=r["transcript"],
            height=500,
            label_visibility="collapsed"
        )

    st.download_button(
        "⬇ Download Transcript",
        r["transcript"],
        file_name="transcript.txt",
    )

    st.download_button(
        "⬇ Download Summary",
        r["summary"],
        file_name="summary.txt",
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("## ✅ Action Items")

        st.write(r["action_items"])

    with c2:

        st.markdown("## 🔑 Key Decisions")

        st.write(r["key_decisions"])

    with c3:

        st.markdown("## ❓ Open Questions")

        st.write(r["open_questions"])

    st.markdown("---")

    st.markdown("## 💬 Chat with Transcript")

    for msg in st.session_state.chat_history:

        if msg["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-user">
                    <b>You:</b><br><br>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="chat-bot">
                    <b>Assistant:</b><br><br>
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    user_input = st.text_input(
        "Ask anything about the transcript"
    )

    ask_btn = st.button("Send")

    if ask_btn and user_input.strip():

        with st.spinner("Thinking..."):

            answer = ask_question(
                r["rag_chain"],
                user_input.strip()
            )

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip()
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

# ─────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────
else:

    st.markdown("## 🎙️ Ready to Analyse")

    st.write(
        "Paste a YouTube URL or local audio file and click Analyse."
    )

    st.info(
        "Supports YouTube links, podcasts, trailers, speeches, and meetings."
    )