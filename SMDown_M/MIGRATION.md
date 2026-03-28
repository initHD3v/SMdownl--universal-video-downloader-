# SMDown_M - Migration Guide

## 📋 Migrasi dari Python ke Native Swift

Dokumen ini menjelaskan proses migrasi aplikasi SMdown dari Python/PySide6 ke native Swift macOS app.

---

## 🎯 Migration Goals

### 1. Functional Equivalence
Mempertahankan semua fitur utama dari versi Python:
- ✅ Download dari YouTube, Facebook, Instagram, X, TikTok
- ✅ Quality selection (4K, 1080p, 720p, 480p, Audio)
- ✅ Download queue management
- ✅ Progress monitoring
- ✅ Clipboard detection
- ✅ Download history
- ✅ Settings management

### 2. Performance Improvements
- **Startup time:** < 1 detik (dari ~2-3 detik di Python)
- **Memory usage:** ~50MB (dari ~150MB di Python)
- **Download speed:** Sama (karena tetap menggunakan yt-dlp)

### 3. User Experience
- Native macOS look & feel
- Smooth animations
- Better system integration
- Smaller app bundle size

---

## 🏗️ Architecture Mapping

### Python → Swift Component Mapping

| Python Component | Swift Component | Notes |
|-----------------|-----------------|-------|
| `app/main.py` | `SMDown_MApp.swift` | App entry point |
| `app/ui/main_window.py` | `ContentView.swift` + `MainViewModel.swift` | Main window & logic |
| `app/downloader/yt_dlp_engine.py` | `YtDlpEngine.swift` | yt-dlp wrapper |
| `app/downloader/queue_manager.py` | `DownloadQueueManager.swift` | Queue management |
| `app/services/clipboard_monitor.py` | `ClipboardMonitorService.swift` | Clipboard monitoring |
| `app/services/history_manager.py` | `HistoryManager.swift` | History storage |
| `app/services/settings_manager.py` | `SettingsManager.swift` | Settings storage |
| `app/services/theme_manager.py` | `ThemeManagerService.swift` | Theme management |
| `app/utils/file_manager.py` | `FileManager.swift` | File utilities |

---

## 🔄 Technology Migration

### 1. UI Framework
```python
# Python (PySide6/Qt)
from PySide6.QtWidgets import QApplication, QMainWindow
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
```

```swift
// Swift (SwiftUI)
@main
struct SMDown_MApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

### 2. Threading Model
```python
# Python (QThread)
class MetadataFetcherThread(QThread):
    def run(self):
        metadata = self.engine.fetch_metadata(url)
```

```swift
// Swift (async/await)
actor YtDlpEngine {
    func fetchMetadata(url: URL) async throws -> VideoMetadata {
        // Non-blocking async
    }
}
```

### 3. Data Models
```python
# Python (dataclass)
@dataclass
class VideoMetadata:
    url: str
    title: str
    duration: int
```

```swift
// Swift (struct)
struct VideoMetadata: Codable {
    let url: String
    let title: String
    let duration: Int
}
```

### 4. State Management
```python
# Python (Qt Signals/Slots)
class MainWindow(QMainWindow):
    download_started = Signal(str)
    download_completed = Signal(str)
```

```swift
// Swift (@Published + Combine)
class MainViewModel: ObservableObject {
    @Published var downloadQueue: [DownloadItem] = []
}
```

---

## 📦 Dependency Migration

### Python Dependencies → Swift Alternatives

| Python Package | Swift Alternative | Purpose |
|---------------|-------------------|---------|
| PySide6 | SwiftUI | UI Framework |
| requests | URLSession | HTTP requests |
| yt-dlp | yt-dlp (CLI) | Video downloader |
| ffmpeg-python | FFmpeg (CLI) | Video processing |

### System Dependencies (Tetap Sama)
```bash
# Kedua versi membutuhkan:
brew install yt-dlp ffmpeg
```

---

## 🎨 UI/UX Migration

### Design Principles

#### Python (PySide6)
```python
# Custom styling dengan CSS-like syntax
button.setStyleSheet("""
    QPushButton {
        background-color: #007AFF;
        border-radius: 10px;
        padding: 12px;
    }
""")
```

#### Swift (SwiftUI)
```swift
Button(action: {}) {
    Text("Download")
        .font(.system(size: 14, weight: .semibold))
        .foregroundStyle(.white)
        .padding(.vertical, 12)
        .background(Color.blue)
        .cornerRadius(10)
}
```

### Component Migration

#### 1. Main Window
```python
# Python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SMdown")
        self.setGeometry(100, 100, 960, 720)
```

```swift
// Swift
struct ContentView: View {
    var body: some View {
        VStack {
            // UI components
        }
        .frame(minWidth: 960, minHeight: 720)
    }
}
```

#### 2. Progress Bar
```python
# Python
progress_bar = QProgressBar()
progress_bar.setStyleSheet("""
    QProgressBar::chunk {
        background-color: #007AFF;
    }
""")
```

```swift
// Swift
ProgressView(value: progress, total: 100)
    .progressViewStyle(.linear)
    .tint(.blue)
```

---

## 🔧 Implementation Checklist

### Phase 1: Core Infrastructure ✅
- [x] Project setup dengan Xcode
- [x] Basic app structure (MVVM)
- [x] Models (VideoMetadata, DownloadItem, etc.)
- [x] yt-dlp engine wrapper
- [x] Download queue manager

### Phase 2: UI Components 🚧
- [x] Main window layout
- [x] URL input section
- [x] Video preview section
- [x] Download queue section
- [x] Control panel
- [ ] Settings view (complete)
- [ ] History view (complete)
- [ ] About dialog

### Phase 3: Services 🚧
- [x] Clipboard monitor
- [x] History manager
- [x] Settings manager
- [x] Theme manager
- [ ] Notification service

### Phase 4: Testing & Polish 📋
- [ ] Unit tests untuk ViewModels
- [ ] Integration tests untuk downloader
- [ ] UI tests
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] User feedback (toasts, notifications)

### Phase 5: Distribution 📋
- [ ] App signing
- [ ] Notarization
- [ ] DMG creation
- [ ] Sparkle update system
- [ ] App Store submission (optional)

---

## 🚀 Build & Run

### Development Build
```bash
# Clone repository
cd SMDown_M

# Open in Xcode
open SMDown_M.xcodeproj

# Atau build via command line
xcodebuild -project SMDown_M.xcodeproj -scheme SMDown_M build
```

### Release Build
```bash
# Archive
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

## 📊 Performance Comparison

| Metric | Python Version | Swift Version | Improvement |
|--------|---------------|---------------|-------------|
| App Size | ~50 MB | ~5 MB | 10x smaller |
| Startup Time | ~2-3 sec | < 1 sec | 2-3x faster |
| Memory Usage | ~150 MB | ~50 MB | 3x less |
| UI Responsiveness | Good | Excellent | Better |
| Download Speed | Same | Same | No change |

---

## ⚠️ Breaking Changes

### 1. System Requirements
- **Python:** macOS 12.0+
- **Swift:** macOS 14.0+ (lebih tinggi)

### 2. Configuration Files
- **Python:** QSettings (INI format)
- **Swift:** UserDefaults (plist format)
- **Migration:** Settings akan di-reset saat upgrade

### 3. History Format
- **Python:** JSON di `~/Library/Application Support/SMdown/history.json`
- **Swift:** JSON di lokasi yang sama (compatible)

---

## 🐛 Known Issues

1. **yt-dlp Path Detection**
   - Issue: yt-dlp harus diinstall via Homebrew
   - Workaround: `brew install yt-dlp`

2. **FFmpeg Path Detection**
   - Issue: FFmpeg harus tersedia di PATH
   - Workaround: `brew install ffmpeg`

3. **Dark Mode Detection**
   - Issue: System theme change tidak selalu terdeteksi
   - Workaround: Restart app

---

## 📚 Resources

### Documentation
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [MVVM in SwiftUI](https://developer.apple.com/tutorials/app-dev-training)

### Tools
- [Xcode 15+](https://developer.apple.com/xcode/)
- [Instruments](https://developer.apple.com/instruments/) (untuk profiling)
- [SwiftFormat](https://github.com/nicklockwood/SwiftFormat) (code formatting)

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 Notes

### Migration Tips
1. **Start with models** - Port data models dulu
2. **Then services** - Implementasi business logic
3. **Finally UI** - Build UI components terakhir
4. **Test incrementally** - Test setiap komponen setelah di-port

### Common Pitfalls
1. **Threading** - Swift actor model berbeda dengan QThread
2. **State management** - @Published vs Qt Signals
3. **File paths** - Gunakan FileManager, bukan string concatenation
4. **Async code** - Gunakan async/await, bukan callback

---

<div align="center">
  <p><b>SMDown_M Migration Guide</b></p>
  <p>v1.0.0 - Last updated: March 2024</p>
</div>
