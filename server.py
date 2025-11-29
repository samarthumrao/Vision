import cv2
import threading
import pyttsx3
import queue
import time
import asyncio
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# --- Configuration ---
DROIDCAM_URL = 0 # Use 0 for local camera

# --- Global State ---
latest_caption = "Waiting for scene..."
latest_frame = None # Store the latest frame for OCR
lock = threading.Lock()

# --- Initialize AI Models ---
print("Loading YOLO model...")
yolo_model = YOLO('yolov8n.pt') 

print("Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# --- TTS Worker ---
tts_queue = queue.Queue()

def tts_worker():
    print("TTS Worker Started")
    while True:
        text = tts_queue.get()
        if text is None: break
        try:
            # Re-initialize engine per utterance
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            tts_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak(text):
    tts_queue.put(text)

# --- Captioning Thread ---
def generate_caption(frame_rgb):
    global latest_caption
    try:
        raw_image = Image.fromarray(frame_rgb)
        inputs = processor(raw_image, return_tensors="pt")
        out = blip_model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        print(f"Caption: {caption}")
        with lock:
            latest_caption = caption
        
        speak(caption)
    except Exception as e:
        print(f"Captioning Error: {e}")

# --- FastAPI App ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_video_frames():
    global latest_frame
    cap = cv2.VideoCapture(DROIDCAM_URL)
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Update global frame for OCR
        with lock:
            latest_frame = frame.copy()

        # YOLO Detection
        results = yolo_model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # BLIP Captioning (Every 150 frames)
        if frame_count % 150 == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            t = threading.Thread(target=generate_caption, args=(frame_rgb,), daemon=True)
            t.start()
        
        frame_count += 1

        # Encode for streaming
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(get_video_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/status")
async def get_status():
    with lock:
        return JSONResponse(content={"caption": latest_caption})

import pytesseract

# Set Tesseract path (Update this if your installation is different)
# Common path on Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.post("/read_text")
async def read_text():
    """
    Performs OCR on the latest captured frame.
    """
    global latest_frame
    
    frame_to_process = None
    with lock:
        if latest_frame is not None:
            frame_to_process = latest_frame.copy()
    
    if frame_to_process is None:
        return JSONResponse(content={"status": "error", "message": "No video frame available"})

    try:
        # --- Preprocessing for Better OCR ---
        # 1. Convert to Grayscale
        gray = cv2.cvtColor(frame_to_process, cv2.COLOR_BGR2GRAY)
        
        # 2. Resize (Upscale) - Tesseract works better on larger text
        scale_percent = 200 # Percent of original size
        width = int(gray.shape[1] * scale_percent / 100)
        height = int(gray.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(gray, dim, interpolation = cv2.INTER_CUBIC)

        # 3. Apply Thresholding (Binarization) to separate text from background
        # Otsu's thresholding is usually good for text
        _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Debug: Save the processed image to check quality
        cv2.imwrite("debug_ocr.jpg", thresh)
        
        # Run OCR
        # --psm 6 assumes a single uniform block of text. 
        # --psm 3 is fully automatic page segmentation (default).
        # --psm 11 is sparse text.
        custom_config = r'--oem 3 --psm 6' 
        text = pytesseract.image_to_string(thresh, config=custom_config)
        clean_text = text.strip()
        
        if clean_text:
            print(f"OCR Text: {clean_text}")
            speak(f"Reading: {clean_text}")
            return JSONResponse(content={"status": "success", "text": clean_text})
        else:
            print("OCR: No text detected.")
            speak("No text found.")
            return JSONResponse(content={"status": "success", "text": "No text detected"})
            
    except Exception as e:
        print(f"OCR Error: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
