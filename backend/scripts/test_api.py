import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"
THREAD_ID = "test-session-manos"

def send_chat(message: str):
    """
    Sends a chat message to the backend API and prints the AI's response.
    
    Args:
        message (str): The user message to send.
    """
    print(f"\n[Frontend] Sending: '{message}'")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"thread_id": THREAD_ID, "message": message}
        )
        response.raise_for_status()
        
        data = response.json()
        messages = data.get("messages", [])
        
        for msg in messages:
            print(f"[Backend AI]: {msg}")
            
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Request failed with {e.response.status_code}")
        print(f"[SERVER DETAILS]: {e.response.text}")
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to the API. Is the FastAPI server running?")
        print("Run this in another terminal first: uvicorn backend.app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")

if __name__ == "__main__":
    print("=======================================")
    print("Testing FastAPI Stateful Memory Engine")
    print("=======================================")
    
    # 1. Ask the first question
    send_chat("what was my last question?")

    
    print("\n=======================================")
    print("Test complete!")
