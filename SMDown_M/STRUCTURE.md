# SMDown_M - Project Structure

## 📁 Complete Folder Structure

```
SMDown_M/
│
├── 📄 README.md                          # Project documentation
├── 📄 MIGRATION.md                       # Migration guide from Python
├── 📄 Package.swift                      # Swift Package Manager config
├── 📄 .gitignore                         # Git ignore rules
│
├── 📁 SMDown_M.xcodeproj/                # Xcode project
│   └── project.pbxproj                   # Project build settings
│
├── 📁 SMDown_M/                          # Main source code
│   │
│   ├── 📁 App/                           # App entry point
│   │   ├── SMDown_MApp.swift             # Main app struct (@main)
│   │   └── AppDelegate.swift             # App lifecycle delegate
│   │
│   ├── 📁 Views/                         # UI components (SwiftUI)
│   │   ├── 📁 Screens/                   # Full screen views
│   │   │   ├── ContentView.swift         # Main window
│   │   │   ├── SettingsView.swift        # Settings screen
│   │   │   ├── HistoryView.swift         # Download history
│   │   │   └── AboutView.swift           # About dialog
│   │   │
│   │   ├── 📁 Components/                # Reusable components
│   │   │   ├── HeaderSection.swift       # App header with logo
│   │   │   ├── URLInputSection.swift     # URL input field
│   │   │   ├── VideoPreviewSection.swift # Video metadata preview
│   │   │   ├── DownloadQueueSection.swift# Queue list view
│   │   │   └── ControlPanel.swift        # Action buttons
│   │   │
│   │   └── 📁 Modifiers/                 # Custom view modifiers
│   │       └── (custom modifiers)
│   │
│   ├── 📁 ViewModels/                    # MVVM ViewModels
│   │   └── MainViewModel.swift           # Main screen state & logic
│   │
│   ├── 📁 Models/                        # Data models
│   │   └── Models.swift                  # All model definitions
│   │       ├── VideoQuality (enum)
│   │       ├── SupportedPlatform (enum)
│   │       ├── VideoMetadata (struct)
│   │       ├── VideoFormat (struct)
│   │       ├── DownloadStatus (enum)
│   │       ├── DownloadItem (struct)
│   │       ├── HistoryItem (struct)
│   │       ├── AppSettings (struct)
│   │       └── ThemeMode (enum)
│   │
│   ├── 📁 Services/                      # Business logic services
│   │   ├── 📁 Clipboard/
│   │   │   └── ClipboardMonitorService.swift
│   │   ├── 📁 History/
│   │   │   └── HistoryManager.swift
│   │   ├── 📁 Settings/
│   │   │   └── SettingsManager.swift
│   │   └── 📁 Theme/
│   │       └── ThemeManagerService.swift
│   │
│   ├── 📁 Downloader/                    # Download engine
│   │   ├── 📁 Engine/
│   │   │   └── YtDlpEngine.swift         # yt-dlp CLI wrapper
│   │   └── 📁 Queue/
│   │       └── DownloadQueueManager.swift # Queue orchestration
│   │
│   ├── 📁 Utils/                         # Utilities & helpers
│   │   ├── FileManager.swift             # File operations
│   │   └── Constants.swift               # App constants & colors
│   │
│   ├── 📁 Resources/                     # Assets & resources
│   │   └── 📁 Assets.xcassets/           # Asset catalog
│   │       ├── Contents.json
│   │       ├── WindowBackground.colorset/
│   │       ├── CardBackground.colorset/
│   │       ├── InputBackground.colorset/
│   │       └── InputBorder.colorset/
│   │
│   ├── 📁 Preview Content/               # SwiftUI preview assets
│   │   └── Preview Assets.xcassets
│   │
│   └── Info.plist                        # App configuration
│
├── 📁 SMDown_MTests/                     # Unit tests
│   └── SMDown_MTests.swift               # Test target
│
└── 📁 logs/                              # Download logs (runtime)
```

---

## 📊 File Count Summary

| Category | Count |
|----------|-------|
| **Swift Source Files** | 22 |
| **UI Views** | 9 |
| **ViewModels** | 1 |
| **Models** | 1 (8 types) |
| **Services** | 4 |
| **Downloader** | 2 |
| **Utils** | 2 |
| **Resources** | 5 color sets |
| **Tests** | 1 |
| **Documentation** | 3 |
| **Config Files** | 4 |
| **Total** | **54 files** |

---

## 🏗️ Architecture Layers

### 1. **App Layer** (`App/`)
Entry point dan app lifecycle management.

### 2. **Presentation Layer** (`Views/`, `ViewModels/`)
- **Views:** SwiftUI views untuk UI
- **ViewModels:** State management dengan MVVM pattern

### 3. **Domain Layer** (`Models/`)
Data models dan business entities.

### 4. **Service Layer** (`Services/`)
Business logic services:
- Clipboard monitoring
- History management
- Settings persistence
- Theme switching

### 5. **Infrastructure Layer** (`Downloader/`, `Utils/`)
- yt-dlp engine wrapper
- Download queue management
- File operations

---

## 🔄 Data Flow

```
User Action (View)
    ↓
ViewModel (State Update)
    ↓
Service/Downloader (Business Logic)
    ↓
Model (Data)
    ↓
ViewModel (State Update via @Published)
    ↓
View (Auto UI Update via SwiftUI)
```

---

## 📦 Key Components

### Main Components

#### 1. `SMDown_MApp.swift`
```swift
@main
struct SMDown_MApp: App {
    @StateObject private var appContainer = AppContainer()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appContainer)
        }
    }
}
```

#### 2. `ContentView.swift`
Main window dengan sections:
- Header
- URL Input
- Video Preview
- Download Queue
- Control Panel

#### 3. `MainViewModel.swift`
State management untuk main screen:
- URL input binding
- Quality selection
- Download queue
- Metadata fetching

#### 4. `YtDlpEngine.swift`
Actor-based yt-dlp wrapper:
- Fetch metadata
- Download video
- Progress tracking

#### 5. `DownloadQueueManager.swift`
Queue orchestration:
- Add/remove items
- Pause/resume/cancel
- Concurrent download management

---

## 🎨 Design System

### Color Assets
Located in `Assets.xcassets/`:
- `WindowBackground` - Main window background
- `CardBackground` - Card/panel backgrounds
- `InputBackground` - Text field backgrounds
- `InputBorder` - Input field borders

### Constants
Defined in `Utils/Constants.swift`:
- App info (name, version)
- UI constants (spacing, corner radius)
- Color constants
- Asset identifiers

---

## 🔧 Configuration Files

### `Info.plist`
App configuration:
- Bundle identifier
- Version info
- Usage descriptions (privacy)
- App category

### `Package.swift`
Swift Package Manager dependencies:
- Kingfisher (image caching)

### `.gitignore`
Git ignore rules untuk:
- Xcode build artifacts
- User settings
- macOS system files
- Logs

---

## 📝 Next Steps

### Immediate Tasks
1. [ ] Add Kingfisher SPM dependency via Xcode
2. [ ] Create app icon assets
3. [ ] Add test cases
4. [ ] Implement remaining UI screens

### Future Enhancements
1. [ ] Add Sparkle for auto-updates
2. [ ] Implement notification system
3. [ ] Add widget support
4. [ ] Create DMG installer

---

## 🚀 Opening the Project

### Option 1: Xcode (Recommended)
```bash
cd /Users/initialh/Projects/smdown/SMDown_M
open SMDown_M.xcodeproj
```

### Option 2: Command Line Build
```bash
cd /Users/initialh/Projects/smdown/SMDown_M
xcodebuild -project SMDown_M.xcodeproj -scheme SMDown_M build
```

### Option 3: VS Code with Swift Extension
```bash
cd /Users/initialh/Projects/smdown/SMDown_M
code .
```

---

## 📋 Checklist untuk Development

### Setup ✅
- [x] Project structure created
- [x] Xcode project configured
- [x] Basic source files created
- [x] Asset catalog setup
- [x] Info.plist configured

### To Do 🚧
- [ ] Add app icon
- [ ] Add Kingfisher dependency
- [ ] Implement complete download flow
- [ ] Add error handling
- [ ] Write unit tests
- [ ] Add documentation comments

---

<div align="center">
  <p><b>SMDown_M Project Structure</b></p>
  <p>Native Swift macOS App - v1.0.0</p>
</div>
