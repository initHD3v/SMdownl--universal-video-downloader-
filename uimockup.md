# UI Mockup Specification
## SMdown — macOS

Version: 1.0  
Target: Frontend Development  
Platform: macOS (Apple Silicon)

---

# 1. Overview

Dokumen ini menjelaskan **struktur UI, komponen, layout, warna, dan behavior** dari aplikasi **Retro Video Downloader**.

Tujuan utama desain:

- UI sederhana dan mudah dipahami
- tampilan seperti **retro game console**
- tetap terlihat **elegan dan modern**
- mengikuti prinsip **UI/UX desktop application**

Frontend developer diharapkan mengikuti struktur layout dan hierarchy yang dijelaskan dalam dokumen ini.

---

# 2. UI Layout Structure

Aplikasi menggunakan **single window layout** dengan pembagian area vertikal.

```
┌─────────────────────────────────────────────┐
│ Header / Title Bar                          │
├─────────────────────────────────────────────┤
│ URL Input Section                           │
├─────────────────────────────────────────────┤
│ Video Preview Section                       │
├─────────────────────────────────────────────┤
│ Download Queue Section                      │
├─────────────────────────────────────────────┤
│ Control Panel                               │
└─────────────────────────────────────────────┘
```

Flow interaksi user:

```
Paste URL
↓
Fetch Metadata
↓
Select Format
↓
Download
↓
Monitor Queue
```

---

# 3. Window Specifications

Default window size:

```
Width: 960px
Height: 720px
```

Resizable:

```
Yes
Minimum width: 820px
Minimum height: 640px
```

Window style:

```
Rounded corner panel style
Dark theme
Retro panel borders
```

---

# 4. Color System

## Primary Background

```
#1E1E1E
```

Digunakan untuk:

- background utama aplikasi

---

## Panel Background

```
#2A2A2A
```

Digunakan untuk:

- container panel
- card UI

---

## Accent Color

```
#C84B31
```

Digunakan untuk:

- tombol utama
- highlight aktif

---

## Retro Gold Accent

```
#D4AF37
```

Digunakan untuk:

- border panel
- separator

---

## Text Color

Primary text:

```
#EAEAEA
```

Secondary text:

```
#AAAAAA
```

---

## Success / Progress Color

```
#6FAF5A
```

Digunakan untuk:

- progress bar
- status success

---

# 5. Typography

## Title Font

Recommended:

```
Orbitron
```

Fallback:

```
SF Pro Display
```

---

## UI Font

Recommended:

```
Inter
```

Fallback:

```
SF Pro Text
```

---

Font sizes:

```
Title        20px
Section      16px
Body         14px
Caption      12px
```

---

# 6. Section Specifications

---

# 6.1 Header Section

Purpose:

- Branding
- Application identity

Layout:

```
┌─────────────────────────────────────────┐
│ RETRO VIDEO DOWNLOADER                  │
│ [YouTube] [Facebook] [Instagram] [X]    │
└─────────────────────────────────────────┘
```

Components:

- App title
- Platform icons

Height:

```
70px
```

---

# 6.2 URL Input Section

Purpose:

Tempat user memasukkan URL video.

Layout:

```
┌─────────────────────────────────────────┐
│ [ Paste video URL here............. ]   │
│                     [ FETCH VIDEO ]     │
└─────────────────────────────────────────┘
```

Components:

### URL Input Field

Type:

```
Text Input
```

Placeholder:

```
Paste video URL here...
```

Width:

```
80%
```

---

### Fetch Button

Label:

```
FETCH VIDEO
```

Behavior:

```
Fetch metadata video
```

---

# 6.3 Video Preview Section

Purpose:

Menampilkan informasi video sebelum download.

Layout:

```
┌──────────────────────────────────────────────┐
│ Thumbnail     Title                          │
│               Channel                        │
│               Duration                       │
│                                              │
│               Format Selection               │
│               ( ) 1080p                      │
│               ( ) 720p                       │
│               ( ) 480p                       │
│               ( ) Audio MP3                  │
│                                              │
│                    [ DOWNLOAD ]              │
└──────────────────────────────────────────────┘
```

Components:

### Thumbnail

Size:

```
160 x 90
```

Source:

```
Video metadata
```

---

### Metadata Text

Fields:

- Title
- Channel
- Duration

---

### Format Selection

Type:

```
Radio Button
```

Options:

```
4K
1080p
720p
480p
Audio
```

---

### Download Button

Label:

```
DOWNLOAD
```

Style:

```
Primary accent button
```

---

# 6.4 Download Queue Section

Purpose:

Menampilkan daftar download yang sedang berlangsung.

Layout:

```
Download Queue

1. Video Title
██████████░░░░░░░░
Speed: 3.2MB/s
ETA: 00:24

2. Video Title
Waiting

3. Video Title
Waiting
```

Components:

Queue item:

```
Title
Progress bar
Speed
ETA
Status
```

---

### Progress Bar

Style:

Retro segmented bar.

Example:

```
████████░░░░░░
```

Color:

```
#6FAF5A
```

---

# 6.5 Control Panel

Purpose:

Kontrol download queue.

Layout:

```
┌─────────────────────────────────────────┐
│ [Pause] [Resume] [Cancel] [Settings]    │
│ [History]                               │
└─────────────────────────────────────────┘
```

Components:

Buttons:

```
Pause
Resume
Cancel
Settings
History
```

Button style:

```
Retro console style
```

---

# 7. UI Component Style

## Panel

Style:

```
background: #2A2A2A
border: 2px solid #D4AF37
border-radius: 8px
padding: 16px
```

---

## Buttons

Primary button:

```
background: #C84B31
color: white
border-radius: 6px
padding: 10px 16px
```

Hover:

```
brightness +10%
```

---

## Input Field

Style:

```
background: #1A1A1A
border: 1px solid #444
color: #EAEAEA
padding: 10px
border-radius: 6px
```

---

# 8. Spacing System

Menggunakan **8px grid system**.

Spacing values:

```
8px
16px
24px
32px
```

---

# 9. Interaction Behavior

## Fetch Button

Action:

```
Fetch metadata video
```

State:

```
Loading indicator
```

---

## Download Button

Action:

```
Add video to queue
```

---

## Queue System

State:

```
Waiting
Downloading
Paused
Completed
Error
```

---

# 10. UX Principles Applied

Desain ini mengikuti prinsip berikut:

### Visual Hierarchy

User langsung melihat:

1. URL input
2. video preview
3. download button

---

### Consistency

Semua panel memiliki:

- padding sama
- border sama
- spacing sama

---

### Feedback

User selalu mendapat feedback:

- progress bar
- status download
- ETA

---

### Simplicity

UI hanya menampilkan elemen penting.

---

# 11. Future UI Improvements

Planned enhancements:

- animated progress bar
- LED style indicators
- theme switcher
- download notification
- tray menu support

---

# 12. Developer Notes

Recommended GUI frameworks:

```
PySide6 (Qt)
```

Alternative:

```
CustomTkinter
```

Reason:

PySide6 memiliki kontrol layout dan styling yang lebih kuat untuk UI kompleks.

---

# End of Document
