<div align="center">

# 👁️ See-Sense AI
### A Smart Vision Assistant for the Visually Impaired

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-FF9600?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <a href="#features">Features</a> •
  <a href="#prerequisites">Prerequisites</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#technologies-used">Tech Stack</a>
</p>

</div>

---

## 📖 Overview

**See-Sense AI** is a smart vision assistant designed to empower visually impaired individuals by providing real-time auditory feedback about their surroundings.

By leveraging advanced AI models for object detection, image captioning, and optical character recognition (OCR), the system acts as a **digital pair of eyes**, converting the visual world into audible speech.

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 🕵️‍♂️ **Real-time Detection** | Identifies and locates objects in the video feed using **YOLOv8**. |
| 📝 **Scene Captioning** | Generates descriptive context captions using the **BLIP model**. |
| 📖 **OCR Text Reading** | Extracts and reads aloud text from the environment using **Tesseract**. |
| 🗣️ **Text-to-Speech** | Converts all visual information (captions, object names, text) into speech. |
| 💻 **Web Interface** | User-friendly **React** frontend to view the camera feed and control settings. |
| 🔌 **Robust API** | **FastAPI** backend exposing endpoints for streaming and on-demand reading. |

---

## 🛠️ Technologies Used

### Backend
* **Language:** Python
* **Framework:** FastAPI
* **CV & AI:** OpenCV, PyTorch, YOLOv8, BLIP
* **OCR:** Tesseract

### Frontend
* **Framework:** React
* **Tooling:** Vite, Node.js

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+**
* **Node.js & npm** (for the frontend)
* **Tesseract OCR**
    * Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    * > **⚠️ Note:** The project assumes Tesseract is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`. If installed elsewhere, you **must** update the path in `server.py`.
* **(Optional) DroidCam**: If you intend to use your smartphone as the camera source.

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/samarthumrao/see-sense-ai.git
cd see-sense-ai
````

### 2\. Backend Setup

It is recommended to use a virtual environment.

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3\. Frontend Setup

Navigate to the frontend directory and install dependencies.

```bash
cd frontend
npm install
```

-----

## 🎮 Usage

You can run the system as a full web application or as a standalone Python script.

### Option A: Full System (Web App)

1.  **Start the Backend Server**
    From the root directory:

    ```bash
    python server.py
    ```

    *The server will start at `http://0.0.0.0:8000`*

2.  **Start the Frontend**
    Open a new terminal, navigate to the `frontend` directory:

    ```bash
    npm run dev
    ```

    *Open your browser and navigate to the URL shown (usually `http://localhost:5173`).*

### Option B: Standalone Script

If you prefer a simple desktop window without the web interface:

```bash
python main.py
```

> Press **`q`** to quit the application.

-----

## 🔧 Configuration

### Camera Source

By default, the system uses the local webcam (Index `0`).
To use **DroidCam** or another IP camera:

1.  Open `server.py` (or `main.py`).
2.  Modify the `DROIDCAM_URL` variable with your IP camera URL.

### Tesseract Path

If Tesseract is not installed in the default Windows location:

1.  Open `server.py`.
2.  Update the line: `pytesseract.pytesseract.tesseract_cmd = r'<your-path>'`.

-----

<div align="center"\>

**See-Sense AI** — *Vision for Everyone.*

</div>


