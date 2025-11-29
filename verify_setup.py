import sys

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"[OK] {module_name} imported successfully.")
    except ImportError as e:
        print(f"[FAIL] Could not import {module_name}: {e}")

print("Verifying dependencies...")
check_import("cv2")
check_import("ultralytics")
check_import("transformers")
check_import("torch")
check_import("pyttsx3")
check_import("PIL")

print("\nIf all imports are OK, you are ready to run main.py.")
