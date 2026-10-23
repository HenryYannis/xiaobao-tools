# 🛠 Xiaobao Tools (xiaobao-tools)

🌐 **[简体中文](./README.md) | English**

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/HenryYannis/xiaobao-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/HenryYannis/xiaobao-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/HenryYannis/xiaobao-tools/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Codex Enabled](https://img.shields.io/badge/OpenAI%20Codex-Enabled-green.svg)](https://openai.com/form/codex-for-oss/)

**Xiaobao Tools (xiaobao-tools)** is a highly curated, modular open-source toolkit comprising 20+ Python scripts and Windows configuration tools designed for independent developers, system administrators, and office professionals. The project aims to provide out-of-the-box, lightweight, and highly efficient automation solutions, covering registry optimizations, local network interactive utilities, office productivity tools, and multimedia processing.

---

## 🌟 Key Features

1. **Zero Threshold, Run Instantly**: The majority of the tools are lightweight, single `.py` files. No complex dependencies or database setups needed. Execute with a simple double-click or CLI command.
2. **Diverse Scenarios, Solving Real Needs**: Covers daily office productivity, network management utilities, and Windows system-level policy tweaks.
3. **Continuous Integration**: A GitHub Actions workflow ([`.github/workflows/ci.yml`](./.github/workflows/ci.yml)) runs on every push and PR: `ruff` checks for syntax errors and undefined names, and the unit tests in `tests/` run with `python -m unittest`. The project also features a forward-looking **OpenAI Codex AI-driven Maintenance Plan**.

---

## 🎯 Target Audiences & Scenarios Matrix

This project is not only dedicated to software developers but is highly focused on serving diverse groups of users with distinct automation needs through lightweight scripts. Below are the five typical user cohorts and pain points our tools successfully resolve:

| 🎯 Target User Cohort | 💡 Core Problems Resolved (Pain Points) | 🛠️ Recommended Tools |
| :--- | :--- | :--- |
| 🧑‍🏫 **Educators & Lab Administrators** | Restricting download actions, locking desktop wallpapers, removing Windows lock screen ads, disabling browser offline games; quick cross-device file sharing. | [System Restrictions Center (lab-assistant)](./system/lab-assistant), [Edge-Disable-Downloads](./system/Edge-Disable-Downloads), [Disable-Wallpaper-Change](./system/Disable-Wallpaper-Change), [Remove-Spotlight-Info](./system/Remove-Spotlight-Info), [LAN-File-Share](./network/LAN-File-Share/lan_file_share.py) |
| 🎬 **Content Creators & UI Designers** | Merging audio clips locally, converting image formats to ICO; bulk extracting video frames, screen capturing, and compressing images. | [Image-to-ICO](./productivity/Image-to-ICO), [Audio-Merger](./productivity/Audio-Merger), [Video-Frame-Extractor](./productivity/Video-Frame-Extractor/video_frame_extractor.py), [Image-Compressor](./productivity/Image-Compressor/image_compressor.py), [Screen-Capture](./productivity/Screen-Capture/screen_capture.py) |
| 🧑‍🎓 **Language Learners & Students** | Using local network peer-to-peer vocabulary testing and memorization helper to study English words synchronized with others. | [LAN-Word-Learner](./productivity/LAN-Word-Learner) |
| 🧑‍💻 **Developers & AI Enthusiasts** | Accessing shared AI chat nodes over local network seamlessly; scanning files via AST to build code outlines for precise LLM Code Reviews. | [LAN-AI-Chat](./network/LAN-AI-Chat) (source not yet published / planned), [Code-Structure-Outline-Generator](./productivity/Code-Outline-Generator/code_outline_generator.py) |
| 💼 **Office Workers & Time Managers** | Trying out a "security question password recovery" flow that issues a random temporary password; tracking clipboard history with quick zero-key EN/CN translations, and precise countdown timer. | [temporary_password.py](./productivity/Temp-Password/temp_password.py), [countdown.py](./productivity/Countdown/countdown.py), [Clipboard-Translator](./productivity/Clipboard-Translator/clipboard_translator.py) |

---

## 📂 Modular Tool Matrix Directory

To help you quickly locate what you need, our tools are grouped into the following categories:

### 1. 🛜 Network & LAN Utilities
| Tool Name / Folder | English Tag | Description |
| :--- | :--- | :--- |
| [局域网-Ai对话](./network/LAN-AI-Chat) | `LAN-AI-Chat` | ⚠️ **Source not yet published / planned**: the folder currently only contains a README, an icon and version info — there is no runnable code yet. Planned as a LAN server-client utility for sharing AI chat across devices. |
| [工具-局域网极速文件共享器](./network/LAN-File-Share/lan_file_share.py) | `lan_file_share` | Exposes a beautiful web page for instant LAN file distribution and mobile-to-PC uploads without internet. |
| [端口扫描工具.py](./network/Port-Scanner/port_scanner.py) | `port_scanner` | Scan open ports on a target IP address with multi-threading and common service detection. |
| [网速测试工具.py](./network/Speed-Test/speed_test.py) | `speed_test` | Test network download/upload speed, latency, and packet loss rate. |

### 2. ⭐ Favorites - Most Used Tools
| Tool Name / Folder | English Tag | Description |
| :--- | :--- | :--- |
| [机房教学策略配置工具](./favorites/one-assistant) | `one-assistant` | All-in-one computer lab manager: Edge/Chrome allowlists and desktop start page, offline game and download restrictions, unified lock screen wallpaper, coding environment tweaks. |
| [学生机纪律守护助手](./favorites/student-guard) | `student-guard` | Student PC guard: full-screen warning when the network drops, full-screen warning when a USB drive is plugged in, scheduled evening shutdown. |

### 3. 💻 System & Browser Optimization
| Tool Name / Folder | English Tag | Description |
| :--- | :--- | :--- |
| [System Restrictions Center](./system/lab-assistant) | `lab-assistant` | Unified system policy restrictions manager: wallpaper lock, Spotlight "Learn about this picture" removal, browser offline game blocking, hosts blocking, and pip mirror configuration. |
| [Edge-禁止下载](./system/Edge-Disable-Downloads) | `Edge-Disable-Downloads` | Securely disables the download capability of Microsoft Edge via Registry and Group Policy edits. |
| [Edge-联网控制](./system/Edge-Internet-Control) | `Edge-Internet-Control` | A powerful lower-level script to block or permit MS Edge internet permissions dynamically. |
| [禁止-修改壁纸](./system/Disable-Wallpaper-Change) | `Disable-Wallpaper-Change` | Restricts wallpaper modifications to lock desktop wallpaper, ideal for kiosks or public displays. |
| [移除-了解此图片](./system/Remove-Spotlight-Info) | `Remove-Spotlight-Info` | Instantly removes the distracting "Learn about this picture" spotlight pop-up from Windows lock screens. |
| [系统垃圾清理工具.py](./system/System-Cleanup/system_cleanup.py) | `system_cleanup` | One-click cleanup tool for temporary files, recycle bin, browser cache, system logs, and more. |
| [开机启动项管理工具.py](./system/Startup-Manager/startup_manager.py) | `startup_manager` | View, add, and remove Windows startup programs for system management. |
| [文件清理工具](./system/Delete-Files-Tool/Delete_Files_Tool.py) | `Delete-Files-Tool` | Scans a folder to group files by type and find large files (by default `.sb3` files over 2 MB) and empty folders, then batch-deletes the selected items. Double-check your selection before deleting. |

### 4. 🛠 Office Automation & Productivity
| Tool Name / Script | English Tag | Description |
| :--- | :--- | :--- |
| [工具-图片转图标](./productivity/Image-to-ICO) | `Image-to-ICO` | Converts ordinary image formats (PNG/JPG) locally into high-resolution, multi-size Windows `.ico` icons. |
| [工具-音频合并](./productivity/Audio-Merger) | `Audio-Merger` | Scans directories and concatenates multiple audio clips (e.g. MP3 files) effortlessly. |
| [工具-代码结构大纲生成器.py](./productivity/Code-Outline-Generator/code_outline_generator.py) | `code_outline_generator` | Scans files using Python's AST parser to extract classes, functions, and docstrings into a beautiful markdown outline. |
| [工具-简易剪贴板历史翻译器.py](./productivity/Clipboard-Translator/clipboard_translator.py) | `clipboard_translator` | Tracks copy history on the clipboard and delivers instant zero-key EN-CN bilingual translation. |
| [临时密码.py](./productivity/Temp-Password/temp_password.py) | `temp_password.py` | Demo of a "security question password recovery" flow: set a security answer (kept in memory only, gone when the window closes), and once answered correctly it generates an 8–64 character random temporary password with `secrets`, with optional uppercase letters, digits and symbols. |
| [数字倒计时.py](./productivity/Countdown/countdown.py) | `countdown.py` | A lightweight countdown timer with sound notifications precise to the second. |
| [进度条.py](./productivity/Progress-Bar/progress_bar.py) | `progress_bar.py` | An elegant, animated CLI progress bar module designed for command-line developers. |
| [批量文件重命名工具.py](./productivity/Batch-File-Renamer/batch_file_renamer.py) | `batch_file_renamer` | Batch file renamer supporting multiple modes: prefix/suffix, replace, sequence, date, and regex. |
| [Excel批量处理工具.py](./productivity/Excel-Batch-Processor/excel_batch_processor.py) | `excel_batch_processor` | Batch read, merge, filter, and analyze multiple Excel files for office productivity. |
| [工具-局域网单词联机学习器](./productivity/LAN-Word-Learner) | `LAN-Word-Learner` | Local network utility to memorize and test English words synchronously, supporting multi-endpoint data synchronization. |
| [工具-批量视频截图提取器.py](./productivity/Video-Frame-Extractor/video_frame_extractor.py) | `video_frame_extractor` | Grabs frames from local videos sequentially by configurable time intervals or manually via slider. |
| [图片批量压缩工具.py](./productivity/Image-Compressor/image_compressor.py) | `image_compressor` | Batch compress images with customizable quality, resize options, and multiple output formats. |
| [屏幕截图工具.py](./productivity/Screen-Capture/screen_capture.py) | `screen_capture` | Screen capture tool supporting full screen, region, window, and delayed screenshots. |
| [Bitwarden Vault Cleaner & TOTP Migrator](./productivity/Bitwarden-Vault-Cleaner) | `Bitwarden-Vault-Cleaner` | 100% offline, client-side Bitwarden vault deduplication, plaintext password auditing, TOTP QR code migration, and Passkey preservation tool. |

---

## 🤖 OpenAI Codex Maintenance & Integration Plan

As a project maintained by a single core developer, utilizing AI to maximize daily maintenance and QA efficiency is a core focus. We are actively experimenting with integrating **OpenAI Codex & API** into the "xiaobao-tools" software lifecycle across four distinct scenarios:

1. **Automated PR Reviews & Intelligent Refactoring (AI Code Review)**:
    Leverages Codex to automatically audit incoming community PR submissions, identifying memory issues, code smells, or style violations, and posting refactored, PEP-8 compliant suggestions directly inside PR comments.
2. **AI-driven Unit Test Generation (AI Test Coverage)**:
    Uses Codex to analyze input/output boundaries of the 20+ standalone scripts and automatically generate `pytest` regression tests inside the `tests/` directory to assure cross-version Windows compatibility.
3. **Smart Issue Triage & Bug Diagnosis (Traceback Analysis)**:
    Feeds user-submitted terminal traceback logs to Codex, automatically extracting environmental details (e.g. OpenCV version, OS version) and auto-assigning tags like `bug` or `os:windows`.
4. **Automated Multilingual Docs Sync (AI Localization)**:
    Extracts code functions to write docstrings using Codex, and keeps the Chinese and English READMEs completely synchronized with zero translation overhead.

---

## 🚀 Quick Start

### 1. Clone the Repository
Ensure you have Python 3.8+ installed. Clone the repository:
```bash
git clone https://github.com/HenryYannis/xiaobao-tools.git
cd xiaobao-tools
```

### 2. Install Dependencies
While simple scripts run on Python's standard library, complex multi-media/productivity tools require third-party libraries. Install them via:
```bash
pip install -r requirements.txt
```

### 3. Run a Tool
Execute any Python script directly inside your terminal:
```bash
python productivity/Temp-Password/temp_password.py
```

---

## 🤝 Contributing

We heartily welcome community members to share their small Python scripts!
For detailed coding formats and PR checklists, please see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📄 License

This project is licensed under the **MIT License**. You are free to copy, modify, distribute, and commercially utilize these tools, provided copyright notices are retained. See [LICENSE](./LICENSE) for details.
