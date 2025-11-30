import cv2
import threading
import pyttsx3
import queue
from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import time

# --- Configuration ---
# DroidCam URL (Replace with your actual IP and Port from the app)
# DROIDCAM_URL = "http://10.201.58.148:4747/video"
DROIDCAM_URL = 0 # Use 0 for the default camera (DroidCam Client Virtual Camera) 

# --- Initialize AI Models ---
print("Loading YOLO model...")
yolo_model = YOLO('yolov8n.pt') 

print("Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# --- TTS Worker ---
# Queue to hold text to be spoken
tts_queue = queue.Queue()

def tts_worker():
    """
    Worker thread that processes the queue. 
    We re-initialize the engine for each phrase to avoid SAPI5/COM state issues.
    """
    print("TTS Worker Started")
    while True:
        text = tts_queue.get()
        if text is None: # Sentinel value to stop thread
            break
        
        try:
            print(f"Speaking: {text}")
            # Re-initialize engine per utterance for maximum stability on Windows
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
            engine.stop() # Ensure it closes
            del engine # Explicitly delete
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            tts_queue.task_done()

# Start TTS Thread
tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    """Add text to the TTS queue."""
    tts_queue.put(text)

# --- The "Thinking" Thread (Captioning) ---
def generate_caption(frame_rgb):
    try:
        # Convert OpenCV frame to PIL Image
        raw_image = Image.fromarray(frame_rgb)
        
        # Generate Caption
        inputs = processor(raw_image, return_tensors="pt")
        out = blip_model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        print(f"Caption: {caption}")
        speak(caption)
    except Exception as e:
        print(f"Captioning Error: {e}")

# --- The Main Loop (Vision) ---
def main():
    print(f"Connecting to Camera Source: {DROIDCAM_URL}...")
    cap = cv2.VideoCapture(DROIDCAM_URL)

    if not cap.isOpened():
        print("Error: Could not open video stream. Please check DroidCam IP and Port.")
        print("Make sure your phone and PC are on the same Wi-Fi.")
        return

    frame_count = 0
    
    print("Starting video loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # 1. Run YOLO (Fast)
        # verbose=False prevents cluttering the console
        results = yolo_model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # 2. Run Captioning (Every 150 frames ~ 5 seconds at 30fps)
        if frame_count % 150 == 0:
            # Convert to RGB for the AI model
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Start a thread so video doesn't freeze
            # We use a daemon thread so it dies if the main program exits
            t = threading.Thread(target=generate_caption, args=(frame_rgb,), daemon=True)
            t.start()

        cv2.imshow("Smart Vision", annotated_frame)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    # Stop TTS thread
    tts_queue.put(None)

if __name__ == "__main__":
    main()
