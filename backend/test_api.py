"""
test_api.py
-----------
Integration test script for the FastAPI backend.

Steps:
  1. Bootstraps the uvicorn server in a background process
  2. Polls GET /health until online
  3. Uploads downloads/Me at the zoo.wav
  4. Triggers the AI pipeline on the uploaded file
  5. Queries the RAG engine via chat Q&A
  6. Fetches the saved details of the processed meeting
  7. Tears down the background server cleanly

Run from the project root:
    uv run python backend/test_api.py
"""

import os
import sys
import time
import signal
import subprocess
import requests

BASE_URL = "http://localhost:8000"
API_PREFIX = f"{BASE_URL}/api/v1"
TEST_FILE = "downloads/Me at the zoo.wav"


def start_server():
    """Starts the FastAPI app using uvicorn in a background process."""
    print("🚀 Starting FastAPI backend server...")
    
    # Run uvicorn from the backend directory using the current python executable
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return proc


def wait_for_server():
    """Polls the health endpoint until the server is ready, timeout after 15 seconds."""
    print("⏳ Waiting for server to become healthy...")
    start_time = time.time()
    while time.time() - start_time < 15:
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Server is online and healthy!")
                print(f"Health Response: {response.json()}\n")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.5)
        
    print("❌ Timeout: Server failed to start.")
    return False


def run_tests():
    """Executes the sequence of API tests."""
    print("=" * 60)
    print("🎮 RUNNING API INTEGRATION TESTS")
    print("=" * 60)

    # ─────────────────────────────────────────────────────────────────
    # Test 1: Upload File
    # ─────────────────────────────────────────────────────────────────
    print("\n--- [TEST 1] POST /api/v1/meeting/upload ---")
    if not os.path.exists(TEST_FILE):
        print(f"❌ Aborted: Test audio file not found at '{TEST_FILE}'")
        return

    print(f"Uploading file: {TEST_FILE} ...")
    with open(TEST_FILE, "rb") as f:
        files = {"file": (os.path.basename(TEST_FILE), f, "audio/wav")}
        response = requests.post(f"{API_PREFIX}/meeting/upload", files=files)
        
    if response.status_code != 201:
        print(f"❌ Upload failed with status {response.status_code}: {response.text}")
        return
        
    upload_data = response.json()
    print("✅ Upload successful!")
    print(f"Response: {upload_data}")
    meeting_id = upload_data["meeting_id"]

    # ─────────────────────────────────────────────────────────────────
    # Test 2: Summarize Meeting (AI Pipeline)
    # ─────────────────────────────────────────────────────────────────
    print("\n--- [TEST 2] POST /api/v1/meeting/summarize ---")
    print(f"Summarizing meeting_id: {meeting_id} (this triggers Whisper + Mistral)...")
    
    start_time = time.time()
    response = requests.post(
        f"{API_PREFIX}/meeting/summarize",
        json={"meeting_id": meeting_id}
    )
    duration = time.time() - start_time
    
    if response.status_code != 200:
        print(f"❌ Summarization failed with status {response.status_code}: {response.text}")
        return
        
    summary_data = response.json()
    print(f"✅ Summarization complete in {duration:.2f} seconds!")
    print(f"AI-Generated Title: {summary_data['title']}")
    print(f"Summary Snippet   : {summary_data['summary'][:150]}...")
    print(f"Action Items      : {summary_data['action_items']}")
    print(f"Key Decisions     : {summary_data['key_decisions']}")
    print(f"Open Questions    : {summary_data['open_questions']}")

    # ─────────────────────────────────────────────────────────────────
    # Test 3: RAG Chat
    # ─────────────────────────────────────────────────────────────────
    print("\n--- [TEST 3] POST /api/v1/meeting/chat ---")
    question = "Who is speaking and what are they doing?"
    print(f"Asking RAG: '{question}'")
    
    response = requests.post(
        f"{API_PREFIX}/meeting/chat",
        json={"meeting_id": meeting_id, "question": question}
    )
    
    if response.status_code != 200:
        print(f"❌ Chat Q&A failed with status {response.status_code}: {response.text}")
        return
        
    chat_data = response.json()
    print("✅ Chat query successful!")
    print(f"Question: {chat_data['question']}")
    print(f"Answer  : {chat_data['answer']}")

    # ─────────────────────────────────────────────────────────────────
    # Test 4: Get Meeting Details
    # ─────────────────────────────────────────────────────────────────
    print("\n--- [TEST 4] GET /api/v1/meeting/{meeting_id} ---")
    print(f"Retrieving stored meeting details for {meeting_id}...")
    
    response = requests.get(f"{API_PREFIX}/meeting/{meeting_id}")
    
    if response.status_code != 200:
        print(f"❌ Detail retrieval failed with status {response.status_code}: {response.text}")
        return
        
    detail_data = response.json()
    print("✅ Details loaded successfully from disk cache!")
    print(f"Stored Title: {detail_data['title']}")
    print(f"Created At  : {detail_data['created_at']}")
    print("-" * 60)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    # Ensure Mistral API Key is in the environment
    # Try reading from backend/.env if not in os.environ
    if "MISTRAL_API_KEY" not in os.environ:
        from dotenv import load_dotenv
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
        load_dotenv(env_path)
        
    if not os.getenv("MISTRAL_API_KEY") or "your_mistral_api_key" in os.getenv("MISTRAL_API_KEY", ""):
        print("⚠️ Warning: MISTRAL_API_KEY is not configured in backend/.env.")
        print("Please configure your actual API key before running the test script.")
        sys.exit(1)

    server_process = None
    try:
        server_process = start_server()
        if wait_for_server():
            run_tests()
    except KeyboardInterrupt:
        print("\nStopping tests...")
    except Exception as e:
        print(f"\n❌ Error during test runtime: {e}")
    finally:
        if server_process:
            print("\n🛑 Shutting down backend server...")
            try:
                # Terminate process safely
                if sys.platform == "win32":
                    server_process.terminate()
                else:
                    os.kill(server_process.pid, signal.SIGTERM)
                server_process.wait(timeout=5)
                print("👋 Server stopped.")
            except Exception as e:
                print(f"Error stopping server: {e}")
