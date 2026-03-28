# SMDown_M - Native Swift macOS Media Downloader

<div align="center">
  <img src="./assets/logo.png" width="160" height="160" alt="SMdown Logo">
  <h3>🎬 Universal Video Downloader untuk macOS (Native Swift)</h3>
  <p><i>Native Apple Silicon app - Dibangun dengan Swift & SwiftUI</i></p>
</div>

---

## 📋 Project Overview

**SMDown_M** adalah migrasi native dari aplikasi SMdown (Python/PySide6) ke **Swift native macOS app** yang dioptimalkan untuk **Apple Silicon (M1-M4)**.

### Key Improvements dari Versi Python:
- ✅ **100% Native Swift** - Performa optimal untuk Apple Silicon
- ✅ **SwiftUI** - UI modern dengan macOS design principles
- ✅ **Async/Concurrency** - Download manager dengan Swift concurrency
- ✅ **Memory Efficient** - Tidak ada Python overhead
- ✅ **System Integration** - Clipboard, notifications, file system integration yang lebih baik
- ✅ **App Bundle** - Single .app file, mudah di-distribute

---

## 🏗️ Architecture

```
SMDown_M/
├── App/                          # App entry point
│   ├── SMDown_MApp.swift         # Main app struct
│   └── AppDelegate.swift         # App lifecycle
│
├── Views/                        # UI Components
│   ├── Screens/                  # Full screen views
│   │   ├── ContentView.swift
│   │   ├── SettingsView.swift
│   │   ├── HistoryView.swift
│   │   └── AboutView.swift
│   ├── Components/               # Reusable components
│   │   ├── HeaderSection.swift
│   │   ├── URLInputSection.swift
│   │   ├── VideoPreviewSection.swift
│   │   ├── DownloadQueueSection.swift
│   │   └── ControlPanel.swift
│   └── Modifiers/                # Custom modifiers
│
├── ViewModels/                   # MVVM ViewModels
│   └── MainViewModel.swift
│
├── Models/                       # Data models
│   └── Models.swift              # VideoMetadata, DownloadItem, etc.
│
├── Services/                     # Business logic services
│   ├── Clipboard/
│   │   └── ClipboardMonitorService.swift
│   ├── History/
│   │   └── HistoryManager.swift
│   ├── Settings/
│   │   └── SettingsManager.swift
│   └── Theme/
│       └── ThemeManagerService.swift
│
├── Downloader/                   # Download engine
│   ├── Engine/
│   │   └── YtDlpEngine.swift    # yt-dlp wrapper
│   └── Queue/
│       └── DownloadQueueManager.swift
│
├── Utils/                        # Utilities
│   ├── FileManager.swift
│   └── Constants.swift
│
└── Resources/                    # Assets
    └── Assets.xcassets
```

---

## 🎯 Features (MVP)

### Phase 1 - Core Downloader ✅
- [x] Paste video URL
- [x] Auto-detect platform (YouTube, Facebook, Instagram, X, TikTok)
- [x] Fetch video metadata (title, thumbnail, duration, uploader)
- [x] Quality selection (4K, 1080p, 720p, 480p, Audio)
- [x] Download video dengan progress bar
- [x] Download queue management

### Phase 2 - Enhanced Features 🚧
- [ ] Clipboard auto-detection
- [ ] Download history
- [ ] Batch download
- [ ] Pause/Resume download
- [ ] Settings (download path, theme, max concurrent)

### Phase 3 - Advanced Features 📋
- [ ] Playlist download
- [ ] Subtitle download
- [ ] Video trimming
- [ ] Built-in media player
- [ ] Smart media organizer

---

## 🛠️ Tech Stack

### Core
- **Language:** Swift 5.9+
- **UI Framework:** SwiftUI
- **Deployment Target:** macOS 14.0+
- **Architecture:** MVVM

### Dependencies
- **Kingfisher:** Image downloading & caching
- **yt-dlp:** Video downloader engine (via CLI)
- **FFmpeg:** Video processing

### Tools
- **Xcode 15.0+**
- **Swift Package Manager**
- **Homebrew** (untuk yt-dlp & ffmpeg)

---

## 🚀 Getting Started

### ⚠️ Penting: Setup Project

Karena file Xcode project (`.xcodeproj`) tidak dapat di-generate secara otomatis dengan reliable, **ikuti langkah di bawah** untuk membuat project di Xcode:

```bash
# 1. Install dependencies
brew install yt-dlp ffmpeg

# 2. Jalankan setup script
./setup_xcode.sh

# 3. Ikuti instruksi di QUICKSTART.md
```

### Prerequisites
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install yt-dlp dan FFmpeg via Homebrew
brew install yt-dlp ffmpeg
```

### Build & Run

1. **Buat project Xcode** - Ikuti panduan di `QUICKSTART.md` atau jalankan `./setup_xcode.sh`
2. Buka **SMDown_M.xcodeproj** di Xcode
3. Pilih scheme **SMDown_M**
4. Tekan **Cmd + R** untuk run

### Build Release
```bash
# Build release
xcodebuild -project SMDown_M.xcodeproj \
  -scheme SMDown_M \
  -configuration Release \
  -archivePath ./build/SMDown_M.xcarchive \
  archive

# Export .app
xcodebuild -exportArchive \
  -archivePath ./build/SMDown_M.xcarchive \
  -exportPath ./build \
  -exportOptionsPlist ExportOptions.plist
```

---

## 📦 Dependencies

### Swift Package Manager
Tambahkan package dependencies di Xcode:
```
https://github.com/onevcat/Kingfisher.git
```

### System Dependencies (Homebrew)
```bash
brew install yt-dlp ffmpeg
```

---

## 🎨 Design System

### Color Palette
```swift
// Light Mode
Window BG:   #F5F5F7
Card BG:     #FFFFFF
Primary:     #007AFF (Apple Blue)
Success:     #34C759
Warning:     #FF9500
Error:       #FF3B30

// Dark Mode
Window BG:   #1E1E1E
Card BG:     #2C2C2E
Primary:     #0A84FF
Success:     #30D158
Warning:     #FF9F0A
Error:       #FF453A
```

### Typography
- **Title:** SF Pro Display, 24pt, Bold
- **Heading:** SF Pro Display, 16pt, Semibold
- **Body:** SF Pro Text, 14pt, Regular
- **Caption:** SF Pro Text, 12pt, Regular

---

## 📝 Development Guidelines

### Code Style
- Gunakan **SwiftFormat** untuk formatting
- Ikuti **Swift API Design Guidelines**
- Gunakan **async/await** untuk asynchronous code
- Implementasi **MVVM pattern** dengan Combine

### Testing
```bash
# Run tests
xcodebuild test \
  -project SMDown_M.xcodeproj \
  -scheme SMDown_M \
  -destination 'platform=macOS'
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**initialH**
- GitHub: [@initHD3v](https://github.com/initHD3v)
- Email: hidayatfauzi6@gmail.com

---

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Downloader engine
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Kingfisher](https://github.com/onevcat/Kingfisher) - Image caching

---

<div align="center">
  <p><b>SMDown_M</b> v1.0.0 — Native Swift macOS app</p>
  <p>Dibuat dengan ❤️ dan Swift</p>
</div>
