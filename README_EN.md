# 🛠 Xiaobao Tools (xiaobao-tools)

🌐 **[简体中文](./README.md) | English**

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/HenryYannis/xiaobao-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Codex Enabled](https://img.shields.io/badge/OpenAI%20Codex-Enabled-green.svg)](https://openai.com/form/codex-for-oss/)
[![Build Status](https://github.com/HenryYannis/xiaobao-tools/actions/workflows/lint.yml/badge.svg)](https://github.com/HenryYannis/xiaobao-tools/actions)

**Xiaobao Tools (xiaobao-tools)** is a highly curated, modular open-source toolkit comprising 20+ Python scripts and Windows configuration tools designed for independent developers, system administrators, and office professionals. The project aims to provide out-of-the-box, lightweight, and highly efficient automation solutions, covering registry optimizations, local network interactive utilities, office productivity tools, and multimedia processing.

---

## 🌟 Key Features

1. **Zero Threshold, Run Instantly**: The majority of the tools are lightweight, single `.py` files. No complex dependencies or database setups needed. Execute with a simple double-click or CLI command.
2. **Diverse Scenarios, Solving Real Needs**: Covers daily office productivity, network management utilities, and Windows system-level policy tweaks.
3. **Engineering Standard & CI Automation**: Integrated with GitHub Actions CI workflows. Follows PEP 8 coding standards and features a forward-looking **OpenAI Codex AI-driven Maintenance Plan**.

---

## 🎯 Target Audiences & Scenarios Matrix

This project is not only dedicated to software developers but is highly focused on serving diverse groups of users with distinct automation needs through lightweight scripts. Below are the five typical user cohorts and pain points our tools successfully resolve:

| 🎯 Target User Cohort | 💡 Core Problems Resolved (Pain Points) | 🛠️ Recommended Tools |
| :--- | :--- | :--- |
| 🧑‍🏫 **Educators & Lab Administrators** | Restricting download actions, locking desktop wallpapers, removing Windows lock screen ads, disabling browser offline games; quick cross-device file sharing. | [System-Restrictions-Tool](./system/System-Restrictions-Tool), [Edge-Disable-Downloads](./system/Edge-Disable-Downloads), [Disable-Wallpaper-Change](./system/Disable-Wallpaper-Change), [Remove-Spotlight-Info](./system/Remove-Spotlight-Info), [LAN-File-Share](./network/lan_file_share.py) |
| 🎬 **Content Creators & UI Designers** | Merging audio clips locally, converting image formats to ICO; bulk extracting video frames, screen capturing, and compressing images. | [Image-to-ICO](./productivity/Image-to-ICO), [Audio-Merger](./productivity/Audio-Merger), [Video-Frame-Extractor](./productivity/video_frame_extractor.py), [Image-Compressor](./productivity/image_compressor.py), [Screen-Capture](./productivity/screen_capture.py) |
| 🧑‍🎓 **Language Learners & Students** | Using local network peer-to-peer vocabulary testing and memorization helper to study English words synchronized with others. | [LAN-Word-Learner](./productivity/LAN-Word-Learner) |
| 🧑‍💻 **Developers & AI Enthusiasts** | Accessing shared AI chat nodes over local network seamlessly; scanning files via AST to build code outlines for precise LLM Code Reviews. | [LAN-AI-Chat](./network/LAN-AI-Chat), [Code-Structure-Outline-Generator](./productivity/code_outline_generator.py) |
| 💼 **Office Workers & Time Managers** | Generating secure passwords randomly; tracking clipboard history with quick zero-key EN/CN translations, and precise countdown timer. | [temporary_password.py](./productivity/temp_password.py), [countdown.py](./productivity/countdown.py), [Clipboard-Translator](./productivity/clipboard_translator.py) |

---

## 📂 Modular Tool Matrix Directory

To help you quickly locate what you need, our tools are structured into three major category folders:

### 1. 🛜 Network & LAN Utilities
| Tool Name / Folder | English Tag | Description |
| :--- | :--- | :--- |
| [局域网-Ai对话](./network/LAN-AI-Chat) | `LAN-AI-Chat` | A local LAN server-client utility facilitating multi-device AI chats without complex configurations. |
| [工具-局域网极速文件共享器](./network/lan_file_share.py) | `lan_file_share` | Exposes a beautiful web page for instant LAN file distribution and mobile-to-PC uploads without internet. |
| [端口扫描工具.py](./network/port_scanner.py) | `port_scanner` | Scan open ports on a target IP address with multi-threading and common service detection. |
| [网速测试工具.py](./network/speed_test.py) | `speed_test` | Test network download/upload speed, latency, and packet loss rate. |

### 2. 💻 System & Browser Optimization
| Tool Name / Folder | English Tag | Description |
| :--- | :--- | :--- |
| [System Restrictions Center](./system/System-Restrictions-Tool) | `System-Restrictions-Tool` | Unified system policy restrictions manager combining wallpaper lock, desktop Spotlight info removal, and Chrome/Edge offline games disable tools. |
| [Edge-禁止下载](./system/Edge-Disable-Downloads) | `Edge-Disable-Downloads` | Securely disables the download capability of Microsoft Edge via Registry and Group Policy edits. |
| [Edge-联网控制](./system/Edge-Internet-Control) | `Edge-Internet-Control` | A powerful lower-level script to block or permit MS Edge internet permissions dynamically. |
| [禁止-修改壁纸](./system/Disable-Wallpaper-Change) | `Disable-Wallpaper-Change` | Restricts wallpaper modifications to lock desktop wallpaper, ideal for kiosks or public displays. |
| [移除-了解此图片](./system/Remove-Spotlight-Info) | `Remove-Spotlight-Info` | Instantly removes the distracting "Learn about this picture" spotlight pop-up from Windows lock screens. |
| [系统垃圾清理工具.py](./system/system_cleanup.py) | `system_cleanup` | One-click cleanup tool for temporary files, recycle bin, browser cache, system logs, and more. |
| [开机启动项管理工具.py](./system/startup_manager.py) | `startup_manager` | View, add, and remove Windows startup programs for system management. |

### 3. 🛠 Office Automation & Productivity
| Tool Name / Script | English Tag | Description |
| :--- | :--- | :--- |
| [工具-图片转图标](./productivity/Image-to-ICO) | `Image-to-ICO` | Converts ordinary image formats (PNG/JPG) locally into high-resolution, multi-size Windows `.ico` icons. |
| [工具-音频合并](./productivity/Audio-Merger) | `Audio-Merger` | Scans directories and concatenates multiple audio clips (e.g. MP3 files) effortlessly. |
| [工具-代码结构大纲生成器.py](./productivity/code_outline_generator.py) | `code_outline_generator` | Scans files using Python's AST parser to extract classes, functions, and docstrings into a beautiful markdown outline. |
| [工具-简易剪贴板历史翻译器.py](./productivity/clipboard_translator.py) | `clipboard_translator` | Tracks copy history on the clipboard and delivers instant zero-key EN-CN bilingual translation. |
| [临时密码.py](./productivity/temp_password.py) | `temp_password.py` | Generates highly secure, random passwords with customizable lengths and character sets. |
| [数字倒计时.py](./productivity/countdown.py) | `countdown.py` | A lightweight countdown timer with sound notifications precise to the second. |
| [进度条.py](./productivity/progress_bar.py) | `progress_bar.py` | An elegant, animated CLI progress bar module designed for command-line developers. |
| [批量文件重命名工具.py](./productivity/batch_file_renamer.py) | `batch_file_renamer` | Batch file renamer supporting multiple modes: prefix/suffix, replace, sequence, date, and regex. |
| [Excel批量处理工具.py](./productivity/excel_batch_processor.py) | `excel_batch_processor` | Batch read, merge, filter, and analyze multiple Excel files for office productivity. |
| [工具-局域网单词联机学习器](./productivity/LAN-Word-Learner) | `LAN-Word-Learner` | Local network utility to memorize and test English words synchronously, supporting multi-endpoint data synchronization. |
| [工具-批量视频截图提取器.py](./productivity/video_frame_extractor.py) | `video_frame_extractor` | Grabs frames from local videos sequentially by configurable time intervals or manually via slider. |
| [图片批量压缩工具.py](./productivity/image_compressor.py) | `image_compressor` | Batch compress images with customizable quality, resize options, and multiple output formats. |
| [屏幕截图工具.py](./productivity/screen_capture.py) | `screen_capture` | Screen capture tool supporting full screen, region, window, and delayed screenshots. |

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
python productivity/temp_password.py
```

---

## 🤝 Contributing

We heartily welcome community members to share their small Python scripts!
For detailed coding formats and PR checklists, please see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📄 License

This project is licensed under the **MIT License**. You are free to copy, modify, distribute, and commercially utilize these tools, provided copyright notices are retained. See [LICENSE](./LICENSE) for details.
