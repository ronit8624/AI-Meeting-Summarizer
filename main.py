"""
main.py
-------
CLI entry point for the AI Meeting Summarizer.
Pipeline: Audio → faster-whisper + WhisperX + Pyannote → Mistral → RAG
"""

from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions, extract_action_items_as_json
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()


def run_pipeline(source: str, language: str = "english") -> dict:
    print("Starting AI Meeting Summarizer...")

    # Step 1: Audio processing
    chunks = process_input(source)

    # Step 2: Transcription (no diarization)
    print("Skipping diarization — using faster-whisper only...")
    plain_transcript = transcribe_all(chunks, language)
    diarized_transcript = plain_transcript

    print(f"Transcript preview: {plain_transcript[:300]}...")

    # Step 3: Title + Summary
    title   = generate_title(plain_transcript)
    summary = summarize(plain_transcript)

    # Step 4: Structured extraction
    action_items_text = extract_action_items(plain_transcript)
    action_items_json = extract_action_items_as_json(plain_transcript)   # for DB storage
    decisions         = extract_key_decisions(plain_transcript)
    questions         = extract_questions(plain_transcript)

    # Step 5: RAG
    rag_chain = build_rag_chain(plain_transcript)

    return {
        "title":               title,
        "transcript":          plain_transcript,
        "diarized_transcript": diarized_transcript,
        "summary":             summary,
        "action_items":        action_items_text,
        "action_items_json":   action_items_json,
        "key_decisions":       decisions,
        "open_questions":      questions,
        "rag_chain":           rag_chain,
    }


if __name__ == "__main__":
    source   = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    result = run_pipeline(source, language)

    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")

    # Diarized transcript will be same as plain transcript when diarization is disabled
    print(f"\n🎙️ Transcript (first 500 chars):\n{result['diarized_transcript'][:500]}...")
    print("=" * 60)

    # RAG Chat
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}\n")
