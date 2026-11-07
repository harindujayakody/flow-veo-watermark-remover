![VEO3 Watermark Remover](https://github.com/user-attachments/assets/5a99626e-6682-46b9-8e5d-3247b3a72908)

# 🎬 Flow Video Zoom Crop

> A fast, modern CLI tool to **zoom, crop, and batch-process videos** into vertical formats — with a beautiful live terminal dashboard.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/FFmpeg-required-black?style=for-the-badge&logo=ffmpeg">
  <img src="https://img.shields.io/badge/UI-Rich%20CLI-purple?style=for-the-badge">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-green?style=for-the-badge">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"></a>
</p>

---

> [!IMPORTANT]
> ### ⚖️ Responsible Use & Terms of Service Notice
> This utility is provided for personal, educational, and creative workflow purposes on media you own or have explicit rights to edit and modify. Cropping or removing service-generated watermarks from third-party AI platforms (such as Google VideoFX / Veo) to misrepresent authorship or evade terms of service may violate the respective platform's ToS and copyright policies. Use this software responsibly and at your own discretion.

---

## ✨ What is this?

This tool helps you **bulk process videos** by:

- Zooming in (center focus)
- Cropping cleanly to vertical **720x1280 (9:16)**
- Rescaling with high-quality Lanczos interpolation
- Safely confirming batches before processing with dry-run support
- Wrapping everything in a **modern terminal UI** that feels like a native desktop app

---

## 🚀 Features

- ⚡ **Bulk video processing**: Recursively scans directories for video files
- 🧪 **Dry-run mode (`--dry-run`)**: Preview planned encodings and output paths without modifying any files
- 🛡️ **Batch confirmation**: Upfront prompt before beginning bulk re-encoding (bypassable with `-y`)
- ⏩ **Skip options**: Skip previously processed outputs (`--skip-processed`) or files already 720x1280 (`--skip-target-res`)
- 🎯 **Smart zoom + crop pipeline**: Automatically calculates aspect ratios, lanczos scaling, and even pixel boundaries
- 📱 **Optimized for vertical**: Reels, Shorts, and TikTok formats
- 🎨 **Beautiful terminal dashboard**: Real-time progress bars, speed metrics, and task cards
- 📁 **Configurable folders**: Custom input and output directories via `-i` and `-o`

---

## 📦 Requirements

- Python **3.9+**
- `ffmpeg` + `ffprobe` installed on system PATH
- Python dependencies:

```bash
pip install -r requirements.txt
```

### System Requirement: FFmpeg

Make sure `ffmpeg` and `ffprobe` are installed:

```bash
ffmpeg -version
ffprobe -version
```

If not installed:
- **Windows**: `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt update && sudo apt install -y ffmpeg`

---

## ⚙️ Installation

```bash
git clone https://github.com/harindujayakody/flow-veo-watermark-remover.git
cd flow-veo-watermark-remover
pip install -r requirements.txt
```

---

## ▶️ Usage

### Basic Usage

Run inside your video folder:

```bash
python app.py
```

### Dry-run Inspection

Preview what files will be processed without re-encoding:

```bash
python app.py --dry-run
```

### Custom Zoom & Arguments

```bash
# Custom zoom factor (e.g. 1.25x zoom)
python app.py 1.25

# Specify custom input and output directories
python app.py -i ./raw_videos -o ./exported_reels

# Non-interactive mode (skip confirmation)
python app.py -y

# Skip videos whose output already exists
python app.py --skip-processed

# Skip videos that are already 720x1280
python app.py --skip-target-res
```

### CLI Options

| Argument | Description | Default |
|---|---|---|
| `zoom` | Zoom factor multiplier (>= 1.0) | `1.12` |
| `-i`, `--input` | Input directory containing videos | `.` (cwd) |
| `-o`, `--output` | Output directory for cropped videos | `./output` |
| `--dry-run` | Scan and preview video plans without re-encoding | `False` |
| `-y`, `--yes` | Skip interactive confirmation prompt | `False` |
| `--skip-processed` | Skip video if output file already exists | `False` |
| `--skip-target-res` | Skip video if already 720x1280 | `False` |

---

## 🔍 Zoom Guide

| Zoom | Feel |
| ---- | ---- |
| 1.00 | No zoom |
| 1.08 | Subtle |
| 1.12 | Natural (default) |
| 1.18 | Strong |
| 1.25 | Aggressive |

---

## 🧪 Running Unit Tests

Run the test suite with:

```bash
python -m unittest test_app.py
```

---

## 🧾 License

[MIT](LICENSE) © 2026 Harindu Jayakody. Free to use and modify.
