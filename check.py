import os
import sys
from datetime import datetime

# Import your client - ensure the path matches your project structure
try:
    from app.services.firebase_client import FirebaseClient
except ImportError:
    print("Error: Could not find firebase_client.py. Ensure this script is in your root directory.")
    sys.exit(1)

def run_firebase_diagnostic():
    print("=== Firebase Connection Diagnostic ===\n")

    # 1. Check for Credentials File
    creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    if os.path.exists(creds_path):
        print(f"[OK] Credentials file found at: {creds_path}")
    else:
        print(f"[FAIL] Credentials file NOT found at: {creds_path}")
        print("      Please ensure your service account JSON is in the correct folder.")
        return

    # 2. Attempt Initialization
    try:
        FirebaseClient.initialize()
        print("[OK] Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        return

    # 3. Test Firestore Write (The 'Ready to Receive' check)
    print("\nAttempting to send test data to Firestore...")
    test_id = f"test_{int(datetime.now().timestamp())}"
    test_payload = {
        test_id: {
            "message": "Connection test",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    }

    result = FirebaseClient.backup_data("connection_tests", test_payload)
    
    if result.get('success'):
        print(f"[OK] Data successfully received by Firebase!")
        print(f"     Collection: connection_tests")
        print(f"     Document ID: {test_id}")
    else:
        print(f"[FAIL] Could not send data. Error: {result.get('error')}")

if __name__ == "__main__":
    run_firebase_diagnostic()