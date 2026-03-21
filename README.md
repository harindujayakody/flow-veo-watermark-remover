# 🎬 Flow Video Zoom Crop

> A fast, modern CLI tool to **zoom, crop, and batch-process videos** into perfect vertical format — with a beautiful live terminal dashboard.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/FFmpeg-required-black?style=for-the-badge&logo=ffmpeg">
  <img src="https://img.shields.io/badge/UI-Rich%20CLI-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Entry%20Point-app.py-orange?style=for-the-badge">
</p>

---

## ✨ What is this?

This tool helps you **bulk process videos** by:

- Zooming in (center focus)
- Cropping cleanly
- Resizing to **720x1280 (9:16)**
- Keeping everything consistent for mobile formats

All wrapped in a **modern terminal UI** that feels like a real application.

---

## 🚀 Features

- ⚡ Bulk video processing (recursive scan)
- 🎯 Smart zoom + crop pipeline
- 📱 Optimized for vertical (Reels / Shorts / TikTok)
- 🎨 Beautiful live terminal dashboard
- 📊 Real-time progress tracking
- 📂 Metadata-aware processing
- 📁 Automatic `/output` folder
- 🧾 Clean final summary

---

## 🖥️ Live UI Experience

- 🎯 Single **current task card**
- 📊 Live progress bar
- 📂 File details (size, duration, resolution)
- ⚙️ Processing status
- 📈 Final performance summary

---

## 📦 Requirements

- Python **3.9+**
- `ffmpeg` + `ffprobe` installed
- Python dependency:

```bash
pip install -r requirements.txt
````

---

## ⚠️ System Requirement

Make sure ffmpeg is installed:

```bash
ffmpeg -version
```

If not installed:

* Windows → download from [https://ffmpeg.org](https://ffmpeg.org)
* Mac → `brew install ffmpeg`
* Linux → `sudo apt install ffmpeg`

---

## ⚙️ Installation

```bash
git clone https://github.com/harindujayakody/flow-veo-watermark-remover
cd flow-video-zoom-crop
pip install -r requirements.txt
```

---

## ▶️ Usage

Run inside your video folder:

```bash
python app.py
```

### With custom zoom:

```bash
python app.py 1.12
```

---

## 🔍 Zoom Guide

| Zoom | Feel              |
| ---- | ----------------- |
| 1.00 | No zoom           |
| 1.08 | Subtle            |
| 1.12 | Natural (default) |
| 1.18 | Strong            |
| 1.25 | Aggressive        |

---

## 📁 Output

* Saved to:

```
./output/
```

* Folder structure preserved
* Auto-renamed files:

```
video_zoom_1_12.mp4
```

---

## 🧠 How it works

1. Scans all video files recursively
2. Reads metadata using `ffprobe`
3. Applies:

   * aspect-aware scaling
   * zoom factor
   * center crop
4. Encodes via `ffmpeg`
5. Displays live UI
6. Generates final summary

---

## 🎨 Best Terminal Setup

For the best experience:

**Fonts**

* JetBrains Mono
* Cascadia Code
* Fira Code

**Terminals**

* Windows Terminal
* iTerm2
* Warp
* WezTerm

---

## 🛠️ Customization

Edit inside `app.py`:

```python
DEFAULT_ZOOM = 1.12
OUT_W = 720
OUT_H = 1280
```

---

## 💡 Use Cases

* Social media content (Reels / Shorts / TikTok)
* Mobile video formatting
* Batch video processing
* Framing adjustments
* Creator workflows

---

## 🧾 License

MIT License — free to use and modify.

---

## ❤️ Credits

**Built by ChatGPT & Prompted by Harindu**

---
