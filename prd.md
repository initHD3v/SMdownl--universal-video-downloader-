# Product Requirements Document (PRD)

# SMdown — macOS

Version: 1.0  
Target Platform: macOS (Apple Silicon)  
Status: Draft

---

# 1. Product Overview

**Universal Video Downloader** adalah aplikasi desktop untuk macOS yang memungkinkan pengguna mengunduh video dari berbagai platform sosial media melalui satu aplikasi sederhana.

Aplikasi ini dirancang khusus untuk **Apple Silicon (M-series)** dan dibangun menggunakan **Python** dengan GUI modern sehingga memberikan pengalaman yang ringan, cepat, dan intuitif.

Platform yang didukung pada versi awal:

- YouTube
- Facebook
- Instagram
- X (Twitter)

Aplikasi ini menggunakan engine downloader yang stabil untuk memastikan kompatibilitas dengan berbagai sumber video.

---

# 2. Goals

## Primary Goals

1. Memungkinkan user mengunduh video hanya dengan **paste link**.
2. Mendukung berbagai platform video populer.
3. Memberikan opsi **pemilihan kualitas video**.
4. Mendukung **download queue**.
5. Dioptimalkan untuk performa **Apple Silicon**.

## Secondary Goals

- User interface minimal dan elegan.
- Mendukung **batch download**.
- Auto detect platform dari URL.
- Sistem update downloader engine.

---

# 3. Target Users

## Primary Users

- Content creator
- Video editor
- Social media manager
- Researcher / archivist

## Secondary Users

- User umum yang ingin menyimpan video offline.

---

# 4. Core Features

## 4.1 Smart URL Detection

User cukup menempelkan URL video.

Sistem akan otomatis mendeteksi platform video.

Contoh:

| Platform | URL Example |
|--------|-------------|
| YouTube | youtube.com / youtu.be |
| Facebook | facebook.com |
| Instagram | instagram.com |
| X | x.com / twitter.com |

---

## 4.2 Video Metadata Fetch

Setelah link dimasukkan, aplikasi akan mengambil metadata video.

Informasi yang ditampilkan:

- Thumbnail
- Judul video
- Durasi
- Channel / uploader
- Format yang tersedia

---

## 4.3 Quality Selection

User dapat memilih kualitas sebelum download.

Pilihan video:

- 4K
- 1080p
- 720p
- 480p

Pilihan audio:

- MP3
- M4A
- Best Audio

---

## 4.4 Download Queue

User dapat menambahkan beberapa video ke dalam queue download.

Contoh tampilan queue:

```
[1] Video A – Downloading
[2] Video B – Waiting
[3] Video C – Waiting
```

Fitur queue:

- Pause
- Resume
- Cancel
- Reorder queue

---

## 4.5 Progress Monitoring

User dapat melihat status download secara real-time.

Informasi yang ditampilkan:

- Progress bar
- Download speed
- Estimated time remaining
- File size

Contoh tampilan:

```
Downloading...

██████████░░░░░░░ 63%

Speed: 4.2 MB/s
ETA: 00:21
```

---

## 4.6 Batch Download

User dapat memasukkan beberapa URL sekaligus.

Contoh:

```
youtube.com/xxxxx
instagram.com/xxxxx
x.com/xxxxx
```

Sistem akan otomatis membuat queue download.

---

## 4.7 File Management

User dapat menentukan:

- Folder download
- Format nama file
- Overwrite rule

Contoh format nama file:

```
{title}_{resolution}.mp4
```

---

## 4.8 Clipboard Detection

Aplikasi dapat mendeteksi link video yang disalin oleh user.

Jika link terdeteksi, aplikasi menampilkan notifikasi.

Contoh:

```
Video link detected

Download?

[ Yes ] [ Ignore ]
```

---

## 4.9 Download History

Aplikasi menyimpan riwayat download.

Contoh:

```
History

✓ Video A
✓ Video B
✓ Video C
```

Informasi yang disimpan:

- Judul video
- Platform
- Tanggal download
- Lokasi file

---

# 5. Non Functional Requirements

## Performance

- Startup time < 2 detik
- Memory usage rendah
- Optimized untuk Apple Silicon

## Stability

- Error handling yang robust
- Retry download otomatis

## Security

- Tidak menyimpan kredensial user
- Tidak menyimpan cookies tanpa izin user

---

# 6. System Architecture

High-level architecture:

```
                ┌──────────────┐
                │    macOS UI  │
                │  (Python GUI)│
                └──────┬───────┘
                       │
                Controller Layer
                       │
        ┌──────────────┼──────────────┐
        │              │              │
 Metadata Fetch   Download Manager   Queue System
        │              │              │
        └──────────────┴──────────────┘
                       │
                Downloader Engine
                       │
                    yt-dlp
                       │
                     FFmpeg
```

---

# 7. Tech Stack

## Programming Language

Python 3.11+

---

## GUI Framework

### Recommended

PySide6 (Qt)

Keuntungan:

- UI modern
- performa stabil
- banyak komponen GUI
- dukungan macOS baik

---

### Alternative

CustomTkinter

Keuntungan:

- ringan
- cepat dikembangkan

Kelemahan:

- UI lebih terbatas

---

## Downloader Engine

yt-dlp

Keuntungan:

- mendukung 1000+ website
- aktif dikembangkan
- stabil

---

## Video Processing

FFmpeg

Digunakan untuk:

- merge audio + video
- convert format
- extract audio

---

# 8. macOS Packaging

Aplikasi akan dikompilasi menjadi aplikasi macOS `.app`.

Tool:

```
pyinstaller
```

Contoh output:

```
UniversalDownloader.app
```

Optimasi Apple Silicon:

```
--target-arch arm64
```

---

# 9. Project Structure

Rekomendasi struktur project:

```
video-downloader-app
│
├── app
│   ├── main.py
│   │
│   ├── ui
│   │   ├── main_window.py
│   │   └── components
│   │
│   ├── downloader
│   │   ├── yt_dlp_engine.py
│   │   └── queue_manager.py
│   │
│   ├── services
│   │   ├── metadata.py
│   │   └── clipboard_monitor.py
│   │
│   └── utils
│       └── file_manager.py
│
├── assets
│
├── requirements.txt
│
└── build
```

---

# 10. UI Layout

Main window design:

```
-------------------------------------------------

 Universal Video Downloader

-------------------------------------------------

[ Paste video link here ..................... ]

[ Fetch Video ]

-------------------------------------------------

Thumbnail

Title:
Duration:

Quality:

( ) 4K
( ) 1080p
( ) 720p
( ) Audio

[ Download ]

-------------------------------------------------

Download Queue

Video A      65%
Video B      Waiting
Video C      Waiting

-------------------------------------------------
```

---

# 11. Future Features

## Version 2

- Download playlist YouTube
- Download entire channel
- Subtitle download
- Scheduled download

---

## Version 3

- AI auto caption
- Video trimming
- Built-in media player
- Smart media organizer

---

# 12. Risks

## Platform API Changes

Beberapa platform seperti Instagram, Facebook, dan X sering mengubah struktur internal mereka.

Solusi:

- Menggunakan downloader engine yang aktif diperbarui
- Menyediakan update engine otomatis

---

## Legal Considerations

Beberapa platform memiliki Terms of Service terkait pengunduhan video.

Solusi:

- Aplikasi hanya menyediakan tool downloader
- User bertanggung jawab atas penggunaan konten

---

# 13. Success Metrics

Keberhasilan produk diukur melalui:

- Download success rate > 95%
- Crash rate < 1%
- Startup time < 2 detik
- Download speed optimal

---

# 14. MVP Scope

Versi MVP akan mencakup fitur berikut:

✓ Paste video link  
✓ Fetch metadata  
✓ Pilih kualitas  
✓ Download video  
✓ Progress bar  

Fitur berikut akan ditunda:

✗ Batch download  
✗ Download history  
✗ Clipboard monitoring  

---

# 15. Release Strategy

Tahapan pengembangan:

Phase 1 — Core Downloader  
Phase 2 — UI Improvement  
Phase 3 — Queue System  
Phase 4 — Advanced Features
