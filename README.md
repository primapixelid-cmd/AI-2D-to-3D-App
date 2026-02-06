# AI 2D-to-3D Generator App

A powerful and professional desktop application designed to transform 2D images into high-quality 3D models using the **InstantMesh** engine. Built with a modern dark-themed GUI using **PySide6**.

## 🚀 Description
This application provides an intuitive interface for 3D generation. Users can drag and drop images, manage their generated assets, and preview 3D meshes in real-time. It is optimized for both professional workstations and lower-spec machines.

## 🛠️ Features
- **Asset Manager**: Track and manage your renders with visual thumbnails.
- **True Fullscreen Mode**: Focus entirely on your 3D viewport with a single click or shortcut (F11).
- **Control**: Start and stop generation at any time with the dedicated Stop button.
- **Real-time Logging**: Monitor the AI generation process step-by-step.
- **3D Viewport**: Interactive OpenGL-based viewer for immediate feedback.

## 📋 Installation

Follow these steps to set up the project on your local machine:

1. **Clone this repository:**
   ```bash
   git clone [LINK_REPO_ABANG]
   cd "2D to 3D"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the InstantMesh Engine:**
   Since the core engine is heavy, it must be cloned manually into the backend directory:
   ```bash
   cd backend
   git clone https://github.com/TencentARC/InstantMesh.git
   cd ..
   ```

## 💻 Usage
Run the main application using:
```bash
python main.py
```

## ⚡ Specifications & Requirements
- **Recommended**: NVIDIA GPU with CUDA support for fast generation (seconds to minutes).
- **Compatibility**: Includes a **CPU Fallback** mode for systems without a compatible GPU (process will be slower).
- **OS**: Windows (tested), Linux/macOS compatible.

---
*Developed with ❤️ for 3D creators.*
