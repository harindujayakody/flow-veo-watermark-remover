# 🎬 Flow Video Zoom Crop

> A fast, modern CLI tool to **zoom, crop, and batch-process videos** into perfect vertical format — with a beautiful live terminal dashboard.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/FFmpeg-required-black?style=for-the-badge&logo=ffmpeg">
  <img src="https://img.shields.io/badge/UI-Rich%20CLI-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-green?style=for-the-badge">
</p>

---

## ✨ What is this?

This tool helps you **bulk process videos** by:

* Zooming in (center focus)
* Cropping cleanly
* Resizing to **720x1280 (9:16)**
* Keeping everything consistent for mobile formats

All wrapped in a **clean, modern terminal UI** that feels like a real app — not a script.

---

## 🚀 Features

* ⚡ **Bulk video processing** (recursive folder scan)
* 🎯 **Smart zoom + crop pipeline**
* 📱 Optimized for **vertical content (Reels / Shorts / TikTok)**
* 🎨 Beautiful **live terminal dashboard**
* 🧠 Metadata-aware processing (resolution, duration, size)
* 📊 Real-time progress tracking
* 📁 Auto output folder (`/output`)
* 🧾 Clean final summary (stats + performance)

---

## 🖥️ Live UI Experience

You get a real-time dashboard with:

* 🎯 Current task (single clean card)
* 📊 Progress bar
* 📂 File details (size, resolution, duration)
* ⚙️ Processing status
* 📈 Final performance summary

---

## 📦 Requirements

* Python **3.9+**
* `ffmpeg` + `ffprobe` installed
* Python package:

```bash
pip install rich
```

---

## ⚙️ Installation

Just download the script or clone your repo:

```bash
git clone https://github.com/your-username/flow-video-zoom-crop.git
cd flow-video-zoom-crop
```

---

## ▶️ Usage

Run inside your video folder:

```bash
python zoom_crop_ui.py
```

### With custom zoom:

```bash
python zoom_crop_ui.py 1.12
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

* Keeps folder structure
* Auto-renames:

```
video_zoom_1_12.mp4
```

---

## 🧠 How it works

1. Scans all videos recursively
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

For the best experience, use:

* **JetBrains Mono**
* **Cascadia Code**
* **Fira Code**

Recommended terminals:

* Windows Terminal
* iTerm2
* Warp
* WezTerm

---

## ⚠️ Notes

Check ffmpeg:

```bash
ffmpeg -version
```

Supported formats:

```
.mp4 .mov .mkv .avi .webm
```

---

## 🛠️ Customization

Edit inside script:

```python
DEFAULT_ZOOM = 1.12
OUT_W = 720
OUT_H = 1280
```

---

## 💡 Use Cases

* Content creators (Reels / Shorts / TikTok)
* Mobile-first video workflows
* Batch video cleanup
* Framing adjustments
* Social media optimization

---

## 🧾 License

MIT — use it, modify it, build on it.

---

## ❤️ Credits

**Built by ChatGPT & Prompted by Harindu**

---
