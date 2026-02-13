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

## 📚 Panduan Pengelolaan Berkas dengan GitHub

Bagian ini dirancang untuk memudahkan Anda mengelola kode sumber proyek, baik untuk backup maupun saat bekerja di komputer yang berbeda.

### A. Langkah Pertama: Menghubungkan Proyek ke GitHub
*Lakukan ini hanya sekali saat pertama kali ingin meng-upload folder dari laptop ke internet:*

1.  **Inisialisasi Folder**: Ketik `git init` di terminal.
2.  **Siapkan Antrean**: Ketik `git add .` untuk menandai semua file.
3.  **Beri Label**: Ketik `git commit -m "Upload pertama dari IdeaPad"`.
4.  **Hubungkan Link**: Ketik `git remote add origin [LINK_GITHUB_ANDA.git]`.
5.  **Kirim Pertama Kali**: Ketik `git push -u origin master` (Login jika diminta).

### B. Langkah Update: Mengirim Perubahan Baru
*Lakukan ini setiap kali Anda selesai mengubah kode (misal benerin UI atau nambah fitur) agar data di GitHub selalu yang terbaru:*

1.  **Cek Status**: Ketik `git status` untuk melihat file apa saja yang baru diubah.
2.  **Update Antrean**: Ketik `git add .` (tanda titik artinya semua file yang berubah).
3.  **Beri Catatan Update**: Ketik `git commit -m "Deskripsi perubahan, misal: perbaiki tombol stop"`.
4.  **Kirim Perubahan**: Ketik `git push origin master`.

### C. Langkah Sinkron: Mengambil Data di Komputer Lain
*Gunakan ini jika Anda pindah ke komputer baru atau ingin update terbaru:*

1.  **Clone Proyek**: `git clone [LINK_GITHUB_ANDA.git]`.
2.  **Tarik Update**: Jika komputer sudah ada datanya tapi ingin update terbaru, cukup ketik `git pull origin master`.
3.  **Download Mesin**: Karena folder `backend/InstantMesh` tidak ikut di-upload (di-ignore), Anda wajib menjalankan perintah ini di dalam folder `backend/`:
    ```bash
    git clone https://github.com/TencentARC/InstantMesh.git
    ```

---
*Developed with ❤️ for 3D creators.*
