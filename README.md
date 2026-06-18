# 🛠 小宝工具箱 (xiaobao-tools)

🌐 **简体中文 | [English](./README_EN.md)**

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/HenryYannis/xiaobao-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Codex Enabled](https://img.shields.io/badge/OpenAI%20Codex-Enabled-green.svg)](https://openai.com/form/codex-for-oss/)
[![Build Status](https://github.com/HenryYannis/xiaobao-tools/actions/workflows/lint.yml/badge.svg)](https://github.com/HenryYannis/xiaobao-tools/actions)

**小宝工具箱 (xiaobao-tools)** 是一款面向独立开发者、系统管理员和日常办公人员的开源 Python 脚本与系统配置工具箱。项目旨在提供开箱即用、轻量化且高效率的自动化方案，包含系统环境优化、局域网交互游戏、手势识别、多媒体合并以及日常趣味工具等。

---

## 🌟 项目特色

1. **零门槛，开箱即用**：绝大多数工具为单一 `.py` 文件，无复杂配置，极速双击或命令行启动。
2. **场景丰富，解决刚需**：涵盖日常办公、局域网娱乐联机、人机交互体验、多媒体处理、系统底层优化等多维应用场景。
3. **高规范与自动化**：集成了 GitHub Actions 自动化检查流，遵循 PEP 8 代码规范，并规划了完善的 **OpenAI Codex AI 辅助工作流**。

---

## 🎯 用户群体与核心解决需求对照 (Target Audiences & Scenarios Matrix)

本项目不仅面向软件开发者，更致力于通过轻量级的自动化方案，服务于日常生活中各种不同背景、有不同特定需求的用户群体。以下是本项目核心工具所覆盖的六大典型用户与解决场景：

| 🎯 目标用户群体 | 💡 核心解决需求 (痛点) | 🛠️ 推荐小工具 |
| :--- | :--- | :--- |
| 🧑‍🏫 **教育工作者与机房管理员** | 想要在少儿编程课或公共机房中，限制用户随意下载、乱改壁纸，或移除 Windows 锁屏悬浮小广告；禁用浏览器离线游戏；跨端极速分发课件。 | [系统限制控制中心](./system/System-Restrictions-Tool), [Edge-禁止下载](./system/Edge-Disable-Downloads), [禁止-修改壁纸](./system/Disable-Wallpaper-Change), [移除-了解此图片](./system/Remove-Spotlight-Info), [工具-局域网极速文件共享器](./network/lan_file_share.py) |
| 🎬 **新媒体创作者与设计师** | 在本地快速进行多段语音拼接录音，或将图片转为高保真 ICO 图标；等时间步长批量无损截取视频画面帧。 | [工具-图片转图标](./productivity/Image-to-ICO), [工具-音频合并](./productivity/Audio-Merger), [工具-批量视频截图提取器](./vision/video_frame_extractor.py) |
| 🧑‍🎓 **外语学习者与青少年** | 希望和身边的同学在局域网内，通过趣味单词联机对战，在互动娱乐中加深英语单词记忆。 | [局域网-单词对战](./network/LAN-Word-Battle) |
| 🧑‍💻 **独立开发者与 AI 狂热者** | 想要在本地免代理搭建局域网 AI 共享网关；或者一键提取项目所有脚本大纲，供大模型精准进行 Code Review。 | [局域网-Ai对话](./network/LAN-AI-Chat), [工具-代码结构大纲生成器.py](./productivity/code_outline_generator.py) |
| 💼 **普通办公族与效率达人** | 频繁需要随机生成高强度账户临时密码，或者是桌面挂置多功能时钟、精确倒计时；自动记录并一键极速翻译剪贴板文本。 | [临时密码.py](./productivity/temp_password.py), [全时钟.py](./games_and_fun/dashboard_clock.py), [数字倒计时.py](./productivity/countdown.py), [工具-简易剪贴板历史翻译器](./productivity/clipboard_translator.py) |
| 🤖 **极客爱好者与算法探索者** | 想要探秘人手 21 个骨骼点识别底座，或者体验酷炫的绿雨代码雨屏保、纯画笔绘制 3D 玫瑰艺术动画。 | [手势识别.py](./vision/gesture_recognizer.py), [手部跟踪.py](./vision/hand_tracking.py), [黑客特效.py](./games_and_fun/hacker_matrix.py) |

---

## 📂 工具矩阵目录

为了让你方便地检索，我们将所有工具划分为五大核心方向：

### 1. 🛜 局域网与网络联机 (Network & LAN Utilities)
| 工具名称/文件夹 | 英文标识 | 核心功能简介 |
| :--- | :--- | :--- |
| [局域网-Ai对话](./network/LAN-AI-Chat) | `LAN-AI-Chat` | 本地局域网内提供多端 AI 对话的前后端交互工具，实现局域网设备免梯免配置共享 AI 能力。 |
| [局域网-单词对战](./network/LAN-Word-Battle) | `LAN-Word-Battle` | 局域网内与好友进行英语单词记忆和对战的多人联机小游戏，兼顾趣味与学习。 |
| [工具-局域网极速文件共享器](./network/lan_file_share.py) | `lan_file_share` | 本地目录一键变身局域网文件共享中心与免流量极速跨端上传分发服务。 |
| [端口扫描工具.py](./network/port_scanner.py) | `port_scanner` | 扫描指定IP地址的开放端口，支持多线程扫描和常见服务识别。 |
| [网速测试工具.py](./network/speed_test.py) | `speed_test` | 测试网络下载/上传速度、延迟和丢包率的网速测试工具。 |

### 2. 💻 系统管理与浏览器控制 (System & Browser Optimization)
| 工具名称/文件夹 | 英文标识 | 核心功能简介 |
| :--- | :--- | :--- |
| [系统限制控制中心](./system/System-Restrictions-Tool) | `System-Restrictions-Tool` | 一体化系统策略控制工具，集合禁止修改壁纸、移除桌面“了解此图片”、禁止 Chrome 和 Edge 离线小游戏功能。 |
| [Edge-禁止下载](./system/Edge-Disable-Downloads) | `Edge-Disable-Downloads` | 通过注册表与组策略，安全快捷地禁用 Edge 浏览器下载功能，适合公共机器、机房或少儿教学环境。 |
| [Edge-联网控制](./system/Edge-Internet-Control) | `Edge-Internet-Control` | 限制或解除 Edge 浏览器联网权限的实用底层脚本。 |
| [禁止-修改壁纸](./system/Disable-Wallpaper-Change) | `Disable-Wallpaper-Change` | 限制用户修改 Windows 桌面壁纸，防误触/统一企业展示或展台的桌面配置工具。 |
| [移除-了解此图片](./system/Remove-Spotlight-Info) | `Remove-Spotlight-Info` | 一键移除 Windows 聚焦锁屏界面右上方繁琐的”了解此图片”浮窗，让锁屏界面重回极简干净。 |
| [系统垃圾清理工具.py](./system/system_cleanup.py) | `system_cleanup` | 清理临时文件、回收站、浏览器缓存、系统日志等系统垃圾的一键清理工具。 |
| [开机启动项管理工具.py](./system/startup_manager.py) | `startup_manager` | 查看、添加、删除Windows开机启动项的系统管理工具。 |

### 3. 🛠 办公自动化与实用程序 (Office Automation & Productivity)
| 工具名称/脚本 | 英文标识 | 核心功能简介 |
| :--- | :--- | :--- |
| [工具-图片转图标](./productivity/Image-to-ICO) | `Image-to-ICO` | 本地快速将常用图片格式（PNG/JPG）一键转换为 Windows 支持的 `.ico` 图标，支持多分辨率合并。 |
| [工具-音频合并](./productivity/Audio-Merger) | `Audio-Merger` | 快速扫描目录并拼接合并多段音频（如 MP3 拼接）的实用多媒体处理脚本。 |
| [工具-代码结构大纲生成器.py](./productivity/code_outline_generator.py) | `code_outline_generator` | 一键扫描项目，提取其中所有的类、函数定义及文档注释(Docstring)，自动生成精美的项目大纲文档，方便开发者或 AI (Codex) 快速阅读代码架构。 |
| [工具-简易剪贴板历史翻译器.py](./productivity/clipboard_translator.py) | `clipboard_translator` | 自动捕获系统剪贴板历史，提供无缝的免 Key 极速中英互译并支持一键重新复制。 |
| [临时密码.py](./productivity/temp_password.py) | `temp_password.py` | 快速生成包含大小写字母、数字和符号的高强度随机临时密码，保障日常账户安全。 |
| [数字倒计时.py](./productivity/countdown.py) | `countdown.py` | 精确到秒的轻量级数字倒计时及声音提醒程序。 |
| [进度条.py](./productivity/progress_bar.py) | `progress_bar.py` | 提供给终端和命令行开发者使用的优雅、动感命令行进度条输出模块。 |
| [批量文件重命名工具.py](./productivity/batch_file_renamer.py) | `batch_file_renamer` | 支持多种重命名模式（前缀/后缀、替换、序号、日期、正则）的批量文件重命名工具。 |
| [Excel批量处理工具.py](./productivity/excel_batch_processor.py) | `excel_batch_processor` | 批量读取、合并、筛选、统计多个Excel文件的办公效率工具。 |

### 4. 👁 人机交互与视觉算法 (Interaction & Vision Algorithms)
| 工具名称/脚本 | 英文标识 | 核心功能简介 |
| :--- | :--- | :--- |
| [手势识别.py](./vision/gesture_recognizer.py) | `gesture_recognizer.py` | 基于 OpenCV 和 MediaPipe 框架，识别复杂手势并触发特定 Windows 系统快捷操作的演示程序。 |
| [手部跟踪.py](./vision/hand_tracking.py) | `hand_tracking.py` | 快速在摄像头视频流中定位手部 21 个核心关键点，并实时输出三维坐标的基础框架。 |
| [工具-批量视频截图提取器.py](./vision/video_frame_extractor.py) | `video_frame_extractor` | 提供视频载入、滑块精准选帧截图，或配置时间步长全自动无损批量截图导出。 |
| [图片批量压缩工具.py](./vision/image_compressor.py) | `image_compressor` | 批量压缩图片，支持自定义压缩质量、调整尺寸和多种输出格式。 |
| [屏幕截图工具.py](./vision/screen_capture.py) | `screen_capture` | 支持全屏、区域、窗口、延时截图的屏幕截图工具。 |

### 5. 🎮 趣味娱乐与科普教育 (Games & Interactive Edutainment)
| 工具名称/脚本 | 英文标识 | 核心功能简介 |
| :--- | :--- | :--- |
| [井字棋.py](./games_and_fun/tic_tac_toe.py) | `tic_tac_toe.py` | 支持双人对战的经典 GUI（基于 Tkinter）井字棋交互游戏。 |
| [时钟.py](./games_and_fun/clock.py) | `clock.py` | 界面极简精致的桌面数字电子时钟，便于工作区挂置。 |
| [全时钟.py](./games_and_fun/dashboard_clock.py) | `dashboard_clock.py` | 交互功能丰富的仪表盘式全时钟，提供多时区、倒计时、闹钟与状态记录看板。 |
| [黑客特效.py](./games_and_fun/hacker_matrix.py) | `hacker_matrix.py` | 基于 Pygame 的经典《黑客帝国》数字雨特效壁纸与屏幕保护运行脚本。 |
| [玫瑰花程序.py](./games_and_fun/turtle_rose.py) | `turtle_rose.py` | 使用 Python Turtle 画笔绘制的三维立体玫瑰花动画程序，具有极高的几何拟真度。 |
| [破译程序.py](./games_and_fun/cipher_decrypter.py) | `cipher_decrypter.py` | 演示字符置换加密与暴力破解过程的密码学教育科普工具，带你初识密码破译。 |

---

## 🤖 OpenAI Codex 辅助维护与集成计划

作为单一核心开发者维护的开源项目，如何通过 AI 技术提高日常迭代效率，是本项目的研究重点。我们正积极探索如何将 **OpenAI Codex & API** 深入整合到小宝工具箱的维护流程中，主要规划了以下四个应用场景：

1. **自动化 PR 审查与代码重构 (AI Code Review)**：
   利用 Codex API，在社区或维护者提交新的 Python 小工具 Pull Request 时，自动执行静态代码分析，发现“坏味道”（如内存泄露、冗长逻辑），并直接在 PR 评论中提供重构后的代码片段。
2. **一键生成单元测试 (AI-driven TDD)**：
   针对仓库中 20+ 个独立 Python 脚本，使用 Codex 解析其输入和输出，自动在 `tests/` 文件夹下生成基于 `pytest` 的单元测试。这能极大降低个人维护者在 Windows/macOS/Linux 等多平台上进行兼容性测试的成本。
3. **智能 Issue 诊断与标签分类 (Smart Tagging)**：
   通过 Codex 自动解析用户在 Issue 模版中提交的报错日志（Traceback），识别出错所涉模块（如 `mediapipe`、`pygame`）与操作系统，并自动标记对应的 `os:windows`、`module:vision` 标签，进行首轮自动化排查。
4. **多语言文档与注释自动补全 (Automated Localization)**：
   使用 Codex 智能提取新代码中的函数并生成双语的 Docstring 注释。自动保持中英文 `README.md` 的工具目录实时同步，将好用的小工具无缝推广至全球开发者社区。

---

## 🚀 快速上手

### 1. 环境准备
推荐使用 Python 3.8 或以上版本。克隆仓库到本地：
```bash
git clone https://github.com/HenryYannis/xiaobao-tools.git
cd xiaobao-tools
```

### 2. 安装依赖
大部分独立小脚本无外部依赖。如果运行涉及到视觉算法或游戏特效（如 `gesture_recognizer.py`、`hacker_matrix.py` 等），请一键安装相关依赖：
```bash
pip install -r requirements.txt
```
> *(注：我们将逐步为每个需要较多依赖的子文件夹配备独立的 requirements.txt)*

### 3. 运行示例
直接在终端或双击运行你感兴趣的工具：
```bash
python temp_password.py
```

---

## 🤝 参与贡献

如果你想分享你日常编写的趣味 Python 小工具，非常欢迎提交 Pull Request！
具体步骤和代码格式要求请参考 [贡献指南 (CONTRIBUTING.md)](./CONTRIBUTING.md)。

---

## 📄 开源许可证

本项目基于 **MIT License** 开源。你可以自由地学习、修改、商用和分发本项目中的工具，但请保留原作者版权声明。详情请参阅 [LICENSE](./LICENSE)。