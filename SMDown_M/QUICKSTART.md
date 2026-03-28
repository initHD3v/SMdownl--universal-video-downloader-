# SMDown_M - Quick Start Guide

## Prerequisites

1. **Xcode 15.0+** - Install from Mac App Store
2. **Homebrew** - Install from https://brew.sh
3. **System dependencies:**
   ```bash
   brew install yt-dlp ffmpeg
   ```

## Creating the Xcode Project

### Step 1: Create New Project

1. Open Xcode
2. **File > New > Project...** (Cmd+Shift+N)
3. Select **macOS > App**
4. Click **Next**

### Step 2: Project Settings

Fill in:
- **Product Name:** `SMDown_M`
- **Team:** Select your development team
- **Organization Identifier:** `com.smdown`
- **Bundle Identifier:** `com.smdown.app`
- **Interface:** `SwiftUI`
- **Language:** `Swift`
- **Uncheck:** Use Core Data
- **Uncheck:** Include Tests

Click **Create** and save to: `/Users/initialh/Projects/smdown/SMDown_M`

### Step 3: Add Existing Files

1. Right-click in the Project Navigator (left panel)
2. Select **"Add Files to SMDown_M..."**
3. Navigate to `SMDown_M/` folder
4. Select **all .swift files** (Cmd+A)
5. **Important:**
   - ☐ **Uncheck** "Copy items if needed"
   - ☑ **Check** "Add to targets: SMDown_M"
6. Click **Add**

### Step 4: Add Assets

1. Right-click in Project Navigator
2. Select **"Add Files to SMDown_M..."**
3. Select `SMDown_M/Resources/Assets.xcassets`
4. Click **Add**

### Step 5: Configure Info.plist

1. Click on the project in Navigator
2. Select **SMDown_M** target
3. Go to **Info** tab
4. Add these keys:

| Key | Type | Value |
|-----|------|-------|
| LSApplicationCategoryType | String | public.app-category.utilities |
| NSPhotoLibraryUsageDescription | String | SMdown needs access to save downloaded videos to your Photos library |
| NSDownloadsFolderUsageDescription | String | SMdown needs access to save downloaded videos to your Downloads folder |

### Step 5: Build Settings

1. Go to **Build Settings** tab
2. Search for "Deployment Target"
3. Set **macOS Deployment Target** to `14.0`

### Step 6: Add Kingfisher Package

For image caching:

1. **File > Add Packages...**
2. Enter: `https://github.com/onevcat/Kingfisher.git`
3. Select **Up to Next Major Version**
4. Click **Add Package**

### Step 7: Build & Run

1. Select **SMDown_M** scheme
2. Press **Cmd+R** to build and run
3. The app should launch!

---

## Troubleshooting

### "Kingfisher module not found"
- Make sure you added the Swift Package
- Try: File > Packages > Resolve Package Versions

### "yt-dlp not found"
```bash
brew install yt-dlp
```

### "FFmpeg not found"
```bash
brew install ffmpeg
```

### Build errors in Swift files
- Check macOS Deployment Target is 14.0+
- Check Swift version is 5.0+
- Clean build folder: Cmd+Shift+K

---

## Next Steps

1. ✅ Project is set up
2. 🚧 Implement download functionality
3. 🚧 Add error handling
4. 🚧 Test with real video URLs
5. 🚧 Add app icon
6. 🚧 Create distribution build

---

For more details, see:
- `README.md` - Project overview
- `MIGRATION.md` - Migration guide from Python
- `STRUCTURE.md` - Project structure

