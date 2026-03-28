#!/bin/bash
# Setup script for SMDown_M project
# This script helps you set up the Xcode project

set -e

PROJECT_DIR="/Users/initialh/Projects/smdown/SMDown_M"
PROJECT_NAME="SMDown_M"
BUNDLE_ID="com.smdown.app"

echo "🚀 SMDown_M - Xcode Project Setup"
echo "=================================="
echo ""
echo "📁 Project location: $PROJECT_DIR"
echo ""

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed or not in PATH"
    echo "Please install Xcode from the App Store"
    exit 1
fi

echo "✅ Xcode is installed"
echo ""

# Instructions for creating the project
echo "📋 Follow these steps to create the Xcode project:"
echo ""
echo "1. Open Xcode"
echo "2. File > New > Project... (or press Cmd+Shift+N)"
echo "3. Select 'macOS' > 'App' and click Next"
echo "4. Fill in:"
echo "   - Product Name: $PROJECT_NAME"
echo "   - Team: (Your development team)"
echo "   - Organization Identifier: com.smdown"
echo "   - Bundle Identifier: $BUNDLE_ID"
echo "   - Interface: SwiftUI"
echo "   - Language: Swift"
echo "   - Uncheck 'Use Core Data'"
echo "   - Uncheck 'Include Tests'"
echo "5. Click Create and save to: $PROJECT_DIR"
echo ""
echo "6. After project is created, add the existing files:"
echo "   - Right-click on the project navigator"
echo "   - Select 'Add Files to SMDown_M...'"
echo "   - Navigate to $PROJECT_DIR/$PROJECT_NAME"
echo "   - Select all .swift files (Cmd+A)"
echo "   - Make sure 'Copy items if needed' is UNCHECKED"
echo "   - Make sure 'Add to targets: SMDown_M' is CHECKED"
echo "   - Click Add"
echo ""
echo "7. Add Assets.xcassets:"
echo "   - Right-click on the project navigator"
echo "   - Select 'Add Files to SMDown_M...'"
echo "   - Select $PROJECT_DIR/$PROJECT_NAME/Resources/Assets.xcassets"
echo "   - Click Add"
echo ""
echo "8. Configure Info.plist:"
echo "   - Click on the project in the navigator"
echo "   - Select the SMDown_M target"
echo "   - Go to 'Info' tab"
echo "   - Add these keys:"
echo "     - LSApplicationCategoryType = public.app-category.utilities"
echo "     - NSPhotoLibraryUsageDescription = SMdown needs access to save downloaded videos"
echo "     - NSDownloadsFolderUsageDescription = SMdown needs access to save videos to Downloads"
echo ""
echo "9. Build settings:"
echo "   - Go to 'Build Settings' tab"
echo "   - Search for 'Deployment Target'"
echo "   - Set macOS Deployment Target to 14.0"
echo ""
echo "10. Run the app:"
echo "    - Select the SMDown_M scheme"
echo "    - Press Cmd+R to build and run"
echo ""
echo "=================================="
echo "📦 Don't forget to install dependencies:"
echo ""
echo "   brew install yt-dlp ffmpeg"
echo ""
echo "   For Kingfisher (image caching):"
echo "   - File > Add Packages..."
echo "   - Enter: https://github.com/onevcat/Kingfisher.git"
echo "   - Select latest version"
echo "   - Click Add Package"
echo ""
echo "=================================="
echo ""

# Create a quick start guide file
cat > "$PROJECT_DIR/QUICKSTART.md" << 'EOF'
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

EOF

echo "✅ Quick start guide created: $PROJECT_DIR/QUICKSTART.md"
echo ""
echo "📖 Open QUICKSTART.md for detailed instructions"
echo ""
