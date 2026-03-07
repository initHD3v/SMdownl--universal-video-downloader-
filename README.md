# SMdown - Universal Video Downloader for macOS

<div align="center">

🎬 **Universal Video Downloader untuk macOS (Apple Silicon)**

</div>

---

## 📖 Deskripsi

SMdown adalah aplikasi desktop untuk macOS yang memungkinkan Anda mengunduh video dari berbagai platform sosial media melalui satu aplikasi yang sederhana dan elegan.

### Platform yang Didukung

- ✅ YouTube
- ✅ Facebook
- ✅ Instagram
- ✅ X (Twitter)
- ✅ TikTok

---

## ✨ Fitur

### MVP (Versi 1.0)
- 📥 Paste video link & fetch metadata
- 🎬 Tampilkan informasi video (judul, durasi, uploader, thumbnail)
- 📺 Pilih kualitas video (4K, 1080p, 720p, 480p)
- 🎵 Download audio only (MP3, M4A)
- 📊 Real-time progress monitoring
- 📁 Custom output directory

### Coming Soon
- ⏳ Download queue dengan pause/resume
- 📋 Batch download (multiple URLs)
- 📜 Download history
- 📋 Clipboard auto-detection
- 🎵 Extract subtitle

---

## 🚀 Instalasi

### Prerequisites

- macOS 12.0+ (Apple Silicon recommended)
- Python 3.11+
- FFmpeg

### 1. Install FFmpeg

```bash
# Menggunakan Homebrew
brew install ffmpeg

# Atau download dari https://ffmpeg.org/download.html
```

### 2. Clone & Install Dependencies

```bash
# Clone repository
cd smdown

# Buat virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📖 Cara Menggunakan

### 1. Jalankan Aplikasi

```bash
python app/main.py
```

### 2. Download Video

1. **Paste URL** video ke dalam input field
2. Klik **Fetch** untuk mengambil informasi video
3. Pilih **kualitas** yang diinginkan
4. Pilih **folder** penyimpanan (opsional)
5. Klik **Download Video**

### 3. Batch Download

Paste multiple URLs (satu per line):
```
https://youtube.com/watch?v=xxxxx
https://instagram.com/p/xxxxx
https://x.com/user/status/xxxxx
```

---

## 🏗️ Struktur Project

```
smdown/
├── app/
│   ├── main.py                 # Entry point
│   ├── ui/
│   │   ├── main_window.py      # Main window UI
│   │   └── components/         # UI components
│   ├── downloader/
│   │   ├── yt_dlp_engine.py    # yt-dlp wrapper
│   │   └── queue_manager.py    # Download queue
│   ├── services/
│   │   └── clipboard_monitor.py # Clipboard detection
│   └── utils/
│       └── file_manager.py     # File utilities
├── assets/                     # App assets
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| GUI Framework | PySide6 (Qt 6) |
| Downloader Engine | yt-dlp |
| Video Processing | FFmpeg |
| Packaging | PyInstaller |

---

## 📦 Build .app Bundle

Untuk membuat aplikasi macOS `.app`:

```bash
# Install pyinstaller
pip install pyinstaller

# Build untuk Apple Silicon
pyinstaller --target-arch arm64 --windowed --name "SMdown" --icon=assets/icon.icns app/main.py
```

Output akan berada di `dist/SMdown.app`

---

## ⚙️ Konfigurasi

### Kualitas Video Tersedia

| Kualitas | Resolusi | Keterangan |
|----------|----------|------------|
| 4K | 2160p | Highest quality |
| 1080p | 1920x1080 | Full HD (Recommended) |
| 720p | 1280x720 | HD |
| 480p | 854x480 | Standard |

### Format Audio

- **Best Audio**: Highest quality audio
- **MP3**: Compatible format
- **M4A**: Apple format

---

## 🔧 Troubleshooting

### FFmpeg not found

```bash
# Pastikan FFmpeg terinstall
brew install ffmpeg

# Atau tambahkan ke PATH
export PATH="/usr/local/bin:$PATH"
```

### Download failed untuk platform tertentu

Beberapa platform memerlukan update engine:

```bash
# Update yt-dlp
pip install --upgrade yt-dlp
```

### App tidak bisa dibuka di macOS

Jika muncul warning "App can't be opened":

```bash
# Di System Preferences > Security & Privacy, klik "Open Anyway"
# Atau gunakan command:
xattr -cr /path/to/SMdown.app
```

---

## 📝 Legal Notice

Aplikasi ini disediakan sebagai tool downloader. User bertanggung jawab atas:
- Kepatuhan terhadap Terms of Service masing-masing platform
- Hak cipta dan penggunaan konten yang diunduh
- Penggunaan pribadi yang wajar

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Credits

- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- **FFmpeg**: https://ffmpeg.org/
- **PySide6**: https://doc.qt.io/qtforpython-6/

---

<div align="center">

**SMdown** v1.0 - Made with ❤️ for macOS

</div>
