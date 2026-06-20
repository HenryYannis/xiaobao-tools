# 🛠 项目代码结构与大纲看板 (Code Outline Board)

> 本文档由 **小宝工具箱 - 代码结构大纲生成器** 自动生成。

> 它可以快速提取代码中所有的类、方法、函数及其 Docstring 注释，方便开发者和 AI 进行结构化感知。

---

## 📄 脚本: [games_and_fun\cipher_decrypter.py](./games_and_fun/cipher_decrypter.py)

**📖 模块简介**: 小宝工具箱 - 密码破译模拟器 (Cipher Decrypter)

功能：
- 模拟密码破译的视觉效果
- 显示随机数字雨
- 演示加密和解密过程

使用方法：
- 直接运行即可观看破译动画
- 等待动画结束后显示隐藏信息

注意事项：
- 这是一个娱乐性质的模拟程序
- 仅用于教育和娱乐目的

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `simulate_decryption` | L27 | 模拟密码破译过程 |

---

## 📄 脚本: [games_and_fun\clock.py](./games_and_fun/clock.py)

**📖 模块简介**: 小宝工具箱 - 海龟时钟 (Turtle Clock)

功能：
- 使用 Python Turtle 绘制的模拟时钟
- 实时显示当前时间
- 精美的表盘设计

使用方法：
- 直接运行即可看到时钟
- 关闭窗口退出

注意事项：
- 需要 turtle 库（Python 自带）
- 需要图形界面支持

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `update_time` | L55 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `update_clock_hands` | L64 | 无函数说明文档 |

---

## 📄 脚本: [games_and_fun\dashboard_clock.py](./games_and_fun/dashboard_clock.py)

**📖 模块简介**: 小宝工具箱 - 全屏仪表盘时钟 (Dashboard Clock)

功能：
- 全屏显示的数字时钟
- 支持多时区显示
- 支持倒计时和闹钟功能
- 支持状态记录看板

使用方法：
- 直接运行即可启动全屏时钟
- 按 Escape 键退出全屏

注意事项：
- 需要 tkinter 库（Python 自带）
- 默认使用 ds-digital 字体，如不存在会使用系统默认字体

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `FullscreenClock` | L28 | 无类说明文档 |
| 🔹 *方法 (Method)* | `FullscreenClock.__init__` | L29 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `FullscreenClock._font_available` | L67 | 检查字体是否可用 |
| 🔹 *方法 (Method)* | `FullscreenClock.update_time` | L76 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `FullscreenClock.safe_exit` | L98 | 无函数说明文档 |

---

## 📄 脚本: [games_and_fun\hacker_matrix.py](./games_and_fun/hacker_matrix.py)

**📖 模块简介**: 小宝工具箱 - 黑客帝国数字雨特效 (Hacker Matrix Digital Rain)

功能：
- 经典《黑客帝国》绿色数字雨特效
- 自动适配屏幕分辨率
- 可作为屏幕保护程序使用

使用方法：
- 直接运行即可启动特效
- 按 Escape 键或空格键退出

注意事项：
- 需要安装 pygame 库：pip install pygame
- 默认使用 SimHei 字体，如不存在会使用系统默认字体

作者：小宝科技站 (xbkjz.cn)
日期：2024


> ⚠️ *该脚本中未检测到显式的类或函数定义，可能为纯顺序流脚本。*

---

## 📄 脚本: [games_and_fun\tic_tac_toe.py](./games_and_fun/tic_tac_toe.py)

**📖 模块简介**: 小宝工具箱 - 井字棋游戏 (Tic Tac Toe)

功能：
- 经典的井字棋游戏
- 支持双人对战和人机对战
- 基于 tkinter 的图形界面

使用方法：
- 直接运行即可开始游戏
- 点击格子下棋
- 可切换双人对战/人机对战模式

注意事项：
- 需要 tkinter 库（Python 自带）

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `TicTacToe` | L28 | 无类说明文档 |
| 🔹 *方法 (Method)* | `TicTacToe.__init__` | L29 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `TicTacToe.create_widgets` | L51 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `TicTacToe.switch_mode` | L100 | 切换对战模式 |
| 🔹 *方法 (Method)* | `TicTacToe.on_click` | L105 | 处理玩家点击 |
| 🔹 *方法 (Method)* | `TicTacToe.make_move` | L121 | 在指定位置下棋 |
| 🔹 *方法 (Method)* | `TicTacToe.computer_move` | L146 | 电脑AI移动 |
| 🔹 *方法 (Method)* | `TicTacToe.check_winner` | L190 | 检查是否有玩家获胜 |
| 🔹 *方法 (Method)* | `TicTacToe.disable_all_buttons` | L205 | 禁用所有按钮 |
| 🔹 *方法 (Method)* | `TicTacToe.reset_game` | L210 | 重置游戏 |

---

## 📄 脚本: [games_and_fun\turtle_rose.py](./games_and_fun/turtle_rose.py)

**📖 模块简介**: 小宝工具箱 - 海龟玫瑰花 (Turtle Rose)

功能：
- 使用 Python Turtle 绘制精美的玫瑰花
- 三维立体效果
- 动画绘制过程

使用方法：
- 直接运行即可观看绘制过程
- 关闭窗口退出

注意事项：
- 需要 turtle 库（Python 自带）
- 需要图形界面支持
- 代码来源于网络，仅供学习交流

作者：小宝科技站 (xbkjz.cn)
日期：2024


> ⚠️ *该脚本中未检测到显式的类或函数定义，可能为纯顺序流脚本。*

---

## 📄 脚本: [network\LAN-Word-Battle\word_battle.py](./network/LAN-Word-Battle/word_battle.py)

**📖 模块简介**: 小宝工具箱 - 局域网单词对战 (LAN Word Battle)

功能：
- 局域网内多人英语单词对战游戏
- 支持服务端和客户端模式
- 趣味学习英语单词

使用方法：
- 服务端：直接运行，自动获取本机IP
- 客户端：运行后输入服务端IP地址连接

注意事项：
- 需要 tkinter 库（Python 自带）
- 需要 words.txt 单词文件（已内置默认单词）
- 服务端和客户端需要在同一局域网内

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `resource_path` | L39 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `load_words` | L48 | 无函数说明文档 |
| 🏫 **类 (Class)** | `QuizGameApp` | L68 | 无类说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.__init__` | L69 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.center_window` | L105 | 完全保留您的居中逻辑 |
| 🔹 *方法 (Method)* | `QuizGameApp.update_scoreboard` | L114 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.log` | L118 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.setup_host` | L124 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.show_join_dialog` | L139 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.setup_guest` | L152 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.setup_game_gui` | L173 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.reset_game_state` | L212 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.start_local_game` | L225 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.request_restart` | L233 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.check_all_ready_for_restart` | L241 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.update_timer` | L250 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.end_game_and_show_result` | L259 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.check_final_result` | L270 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.display_final_result` | L276 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.next_question` | L290 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.submit_answer` | L307 | 【修复】提交时实时同步分数 |
| 🔹 *方法 (Method)* | `QuizGameApp.start_host_thread` | L329 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.start_guest_thread` | L333 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.host_recv_loop` | L337 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.guest_recv_loop` | L361 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `QuizGameApp.on_closing` | L387 | 无函数说明文档 |

---

## 📄 脚本: [network\lan_file_share.py](./network/lan_file_share.py)

**📖 模块简介**: 小宝工具箱 - 局域网极速文件共享器 (LAN File Share Server)
功能：一键将电脑上的指定目录化身局域网文件共享中心，局域网内的任何手机、平板、电脑只需输入网页地址，
     即可免流量、极速下载电脑上的文件，甚至支持直接在手机浏览器中向电脑上传文件。
受众：教育工作者、教师（一键分发课件）、日常跨平台（手机到电脑）临时传输大文件的办公人员。


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `CustomHTTPRequestHandler` | L31 | 自定义 HTTP 请求处理器，在标准 SimpleHTTPRequestHandler 上提供文件上传能力 |
| 🔹 *方法 (Method)* | `CustomHTTPRequestHandler.do_POST` | L37 | 处理局域网内其他设备上传文件的 POST 请求 |
| 🔹 *方法 (Method)* | `CustomHTTPRequestHandler.list_directory` | L150 | 重写目录列表生成方法，在页面顶部注入一个精致的文件上传 HTML 表单 |
| 🔹 *方法 (Method)* | `CustomHTTPRequestHandler._verify_token` | L247 | 验证请求中的访问令牌 |
| 🏫 **类 (Class)** | `LANShareApp` | L264 | 无类说明文档 |
| 🔹 *方法 (Method)* | `LANShareApp.__init__` | L265 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `LANShareApp.get_local_ip` | L286 | 自动提取电脑所在的局域网真实 IP 地址 |
| 🔹 *方法 (Method)* | `LANShareApp.setup_ui` | L298 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `LANShareApp.select_directory` | L344 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `LANShareApp.start_http_server` | L353 | 开启 HTTP 共享服务的线程核心逻辑 |
| 🏫 **类 (Class)** | `CustomHTTPHandler` | L358 | 无类说明文档 |
| 🔹 *方法 (Method)* | `CustomHTTPHandler.__init__` | L359 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `LANShareApp.toggle_server` | L375 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `LANShareApp.reset_ui_to_stopped` | L417 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `on_app_closing` | L432 | 无函数说明文档 |

---

## 📄 脚本: [network\port_scanner.py](./network/port_scanner.py)

**📖 模块简介**: 端口扫描工具 (Port Scanner)

功能：
- 扫描指定IP地址的开放端口
- 支持自定义端口范围
- 支持多线程扫描
- 识别常见服务
- 导出扫描结果

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `PortScanner` | L30 | 端口扫描器 |
| 🔹 *方法 (Method)* | `PortScanner.__init__` | L33 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `PortScanner.create_widgets` | L73 | 创建界面组件 |
| 🔹 *方法 (Method)* | `PortScanner.on_common_port_select` | L180 | 选择常用端口 |
| 🔹 *方法 (Method)* | `PortScanner.start_scan` | L192 | 开始扫描 |
| 🔹 *方法 (Method)* | `PortScanner.scan_worker` | L241 | 扫描工作线程 |
| 🔹 *方法 (Method)* | `PortScanner.get_banner` | L281 | 获取Banner |
| 🔹 *方法 (Method)* | `PortScanner.update_progress` | L296 | 更新进度 |
| 🔹 *方法 (Method)* | `PortScanner.stop_scan` | L321 | 停止扫描 |
| 🔹 *方法 (Method)* | `PortScanner.add_result` | L330 | 添加结果 |
| 🔹 *方法 (Method)* | `PortScanner.clear_results` | L334 | 清空结果 |
| 🔹 *方法 (Method)* | `PortScanner.export_results` | L344 | 导出结果 |

---

## 📄 脚本: [network\speed_test.py](./network/speed_test.py)

**📖 模块简介**: 网速测试工具 (Speed Test Tool)

功能：
- 测试网络延迟（Ping）
- 测试下载速度（使用公共测速文件）
- 测试上传速度
- 历史记录（自动保存与加载）

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `SpeedTestTool` | L30 | 网速测试工具 |
| 🔹 *方法 (Method)* | `SpeedTestTool.__init__` | L33 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `SpeedTestTool.create_widgets` | L67 | 创建界面组件 |
| 🔹 *方法 (Method)* | `SpeedTestTool.get_server_by_name` | L154 | 根据名称获取服务器 |
| 🔹 *方法 (Method)* | `SpeedTestTool.start_test` | L161 | 开始测试 |
| 🔹 *方法 (Method)* | `SpeedTestTool.run_test` | L195 | 运行测试 |
| 🔹 *方法 (Method)* | `SpeedTestTool.test_ping` | L268 | 测试延迟 — 使用指定服务器的端口 |
| 🔹 *方法 (Method)* | `SpeedTestTool.test_download` | L297 | 测试下载速度 — 使用 socket 接收数据来评估带宽 |
| 🔹 *方法 (Method)* | `SpeedTestTool.test_upload` | L342 | 测试上传速度 — 发送数据并测量传输速率 |
| 🔹 *方法 (Method)* | `SpeedTestTool.show_ping_result` | L379 | 显示延迟结果 |
| 🔹 *方法 (Method)* | `SpeedTestTool.show_download_result` | L387 | 显示下载结果 |
| 🔹 *方法 (Method)* | `SpeedTestTool.show_upload_result` | L394 | 显示上传结果 |
| 🔹 *方法 (Method)* | `SpeedTestTool.update_status` | L401 | 更新状态 |
| 🔹 *方法 (Method)* | `SpeedTestTool.testing_complete` | L405 | 测试完成 |
| 🔹 *方法 (Method)* | `SpeedTestTool.stop_test` | L412 | 停止测试 |
| 🔹 *方法 (Method)* | `SpeedTestTool.add_history` | L421 | 添加历史记录 |
| 🔹 *方法 (Method)* | `SpeedTestTool.load_history` | L431 | 加载历史记录 |
| 🔹 *方法 (Method)* | `SpeedTestTool.save_history` | L442 | 保存历史记录到文件 |

---

## 📄 脚本: [productivity\Audio-Merger\audio_merger.py](./productivity/Audio-Merger/audio_merger.py)

**📖 模块简介**: 小宝工具箱 - 音频合并工具 (Audio Merger)

功能：
- 批量合并多个音频文件
- 支持 MP3、WAV、OGG 等格式
- 图形界面操作

使用方法：
- 选择包含音频文件的目录
- 点击合并按钮

注意事项：
- 需要安装 pydub：pip install pydub
- 需要 ffmpeg 支持（可将 ffmpeg.exe 放在脚本同目录）
- Windows 系统下会自动隐藏 subprocess 窗口

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `_hidden_popen` | L37 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `validate_path` | L58 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `merge_mp3_files` | L62 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `pick_dir` | L94 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `pick_out` | L100 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `gui` | L111 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `start` | L142 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `work` | L157 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `update_prog` | L158 | 无函数说明文档 |

---

## 📄 脚本: [productivity\batch_file_renamer.py](./productivity/batch_file_renamer.py)

**📖 模块简介**: 批量文件重命名工具 (Batch File Renamer)

功能：
- 支持多种重命名模式：添加前缀/后缀、替换字符、序号重命名、日期重命名
- 支持预览重命名结果
- 支持撤销操作（基于重命名后的实际路径）
- 支持正则表达式匹配

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `BatchFileRenamer` | L27 | 批量文件重命名器 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.__init__` | L30 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.create_widgets` | L53 | 创建界面组件 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.update_mode_options` | L188 | 更新模式选项显示 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.select_directory` | L206 | 选择目录 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.load_files` | L213 | 加载文件列表 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.update_file_list` | L247 | 更新文件列表显示 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.preview_rename` | L255 | 预览重命名结果 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.execute_rename` | L299 | 执行重命名 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.undo_rename` | L334 | 撤销重命名 — 使用重命名映射中的新路径恢复原名 |
| 🔹 *方法 (Method)* | `BatchFileRenamer.clear_list` | L361 | 清空列表 |

---

## 📄 脚本: [productivity\clipboard_translator.py](./productivity/clipboard_translator.py)

**📖 模块简介**: 小宝工具箱 - 简易剪贴板历史翻译器 (Clipboard History & Quick Translator)
功能：后台静默监听系统剪贴板，自动记录历史复制内容，提供一键翻译（中英互译，基于免 key 翻译 API）并一键写回剪贴板。
受众：阅读外文文献的学生、处理跨国业务/英文报告的办公族、频繁复制粘贴的人员。


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `ClipboardTranslatorApp` | L21 | 无类说明文档 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.__init__` | L22 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.setup_ui` | L41 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.detect_language` | L83 | 改进的语言检测：统计 CJK 字符占比来判断语言方向。 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.monitor_clipboard` | L117 | 主循环：每隔 500 毫秒轮询系统剪贴板，检测文本变更 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.update_listbox` | L140 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.copy_selected_to_clipboard` | L148 | 双击条目，重新将其完整复制回系统剪贴板 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.copy_translation` | L160 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.clear_history` | L170 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.translate_selected` | L176 | 多线程调用免费 MyMemory API 进行翻译，防 GUI 卡顿 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.run_translation` | L191 | 调用免费 MyMemory API 进行翻译，使用改进的语言检测 |
| 🔹 *方法 (Method)* | `ClipboardTranslatorApp.show_translation_result` | L218 | 无函数说明文档 |

---

## 📄 脚本: [productivity\countdown.py](./productivity/countdown.py)

**📖 模块简介**: 小宝工具箱 - 倒计时器 (Countdown Timer)

功能：
- 支持自定义倒计时时长（小时/分钟/秒）
- 倒计时结束时发出声音提醒
- 全屏倒计时显示
- 支持暂停和恢复

使用方法：
- 直接运行即可设置倒计时
- 按 Escape 键退出全屏

注意事项：
- 需要 tkinter 库（Python 自带）
- 声音提醒使用系统蜂鸣

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `CountdownTimer` | L30 | 无类说明文档 |
| 🔹 *方法 (Method)* | `CountdownTimer.__init__` | L31 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `CountdownTimer.create_widgets` | L53 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `CountdownTimer.set_preset` | L117 | 设置预设时长 |
| 🔹 *方法 (Method)* | `CountdownTimer.start_countdown` | L126 | 开始倒计时 |
| 🔹 *方法 (Method)* | `CountdownTimer.update_countdown` | L153 | 更新倒计时显示 |
| 🔹 *方法 (Method)* | `CountdownTimer.countdown_complete` | L178 | 倒计时完成 — 发出声音提醒 |
| 🔹 *方法 (Method)* | `CountdownTimer.toggle_pause` | L195 | 切换暂停/恢复 |
| 🔹 *方法 (Method)* | `CountdownTimer.reset_countdown` | L210 | 重置倒计时 |

---

## 📄 脚本: [productivity\excel_batch_processor.py](./productivity/excel_batch_processor.py)

**📖 模块简介**: Excel批量处理工具 (Excel Batch Processor)

功能：
- 批量读取多个Excel文件
- 合并多个Excel文件
- 提取指定列数据
- 数据筛选和过滤
- 导出处理结果

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `ExcelBatchProcessor` | L29 | Excel批量处理器 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.__init__` | L32 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.create_widgets` | L45 | 创建界面组件 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.update_options` | L164 | 更新选项显示 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.add_files` | L181 | 添加文件 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.add_directory` | L195 | 添加目录 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.clear_files` | L212 | 清空文件列表 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.load_files` | L218 | 加载文件 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.preview_data` | L234 | 预览数据 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.process_data` | L263 | 处理数据 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.merge_dataframes` | L292 | 合并数据框 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.extract_columns` | L306 | 提取列 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.filter_data` | L326 | 筛选数据 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.calculate_stats` | L364 | 计算统计信息 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.display_result` | L390 | 显示结果 |
| 🔹 *方法 (Method)* | `ExcelBatchProcessor.export_data` | L410 | 导出数据 |

---

## 📄 脚本: [productivity\progress_bar.py](./productivity/progress_bar.py)

**📖 模块简介**: 小宝工具箱 - 命令行进度条 (Progress Bar)

功能：
- 在命令行显示动态进度条
- 支持自定义进度条长度
- 实时更新进度百分比

使用方法：
- 直接运行即可看到进度条效果
- 可作为模块导入使用

注意事项：
- 需要在命令行环境中运行
- 使用 time.sleep 模拟进度，实际使用时可替换为真实任务

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `show_progress_bar` | L26 | 显示进度条 |

---

## 📄 脚本: [productivity\temp_password.py](./productivity/temp_password.py)

**📖 模块简介**: 小宝工具箱 - 临时密码生成器 (Temporary Password Generator)

功能：
- 生成高强度随机临时密码
- 支持自定义密码长度（默认 16 位）
- 支持包含大小写字母、数字和符号
- 使用 secrets 模块确保密码学安全

使用方法：
- 直接运行即可生成密码
- 复制生成的密码使用

注意事项：
- 需要 tkinter 库（Python 自带）
- 生成的密码仅用于临时用途

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `SecurityApp` | L33 | 无类说明文档 |
| 🔹 *方法 (Method)* | `SecurityApp.__init__` | L34 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `SecurityApp.set_security_question` | L68 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `SecurityApp.open_new_window` | L82 | 无函数说明文档 |
| 🏫 **类 (Class)** | `NewPasswordWindow` | L88 | 无类说明文档 |
| 🔹 *方法 (Method)* | `NewPasswordWindow.__init__` | L95 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `NewPasswordWindow.reset_password` | L159 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `NewPasswordWindow.generate_temp_password` | L175 | 使用 secrets 模块生成密码学安全的高强度临时密码 |

---

## 📄 脚本: [system\Disable-Wallpaper-Change\wallpaper_policy_tool.py](./system/Disable-Wallpaper-Change/wallpaper_policy_tool.py)

**📖 模块简介**: 小宝工具箱 - 壁纸修改限制工具 (Wallpaper Policy Tool)

功能：
- 禁止或允许用户修改 Windows 桌面壁纸
- 通过修改注册表策略实现
- 适合公共电脑或展示环境

使用方法：
- 需要以管理员权限运行
- 点击按钮切换壁纸修改权限

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 修改后需要重启资源管理器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `restart_explorer` | L38 | 强制重启资源管理器以应用设置 |
| ⚙️ **函数 (Func)** | `modify_wallpaper_policy` | L53 | 修改注册表以控制壁纸修改权限。 |
| 🏫 **类 (Class)** | `WallpaperToolGUI` | L91 | 无类说明文档 |
| 🔹 *方法 (Method)* | `WallpaperToolGUI.__init__` | L92 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `WallpaperToolGUI.set_policy` | L125 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `main` | L137 | 无函数说明文档 |

---

## 📄 脚本: [system\Edge-Disable-Downloads\edge_download_manager.py](./system/Edge-Disable-Downloads/edge_download_manager.py)

**📖 模块简介**: 小宝工具箱 - Edge 下载管理器 (Edge Download Manager)

功能：
- 禁用或启用 Edge 浏览器的下载功能
- 通过修改注册表实现
- 适合公共电脑或教学环境

使用方法：
- 需要以管理员权限运行
- 点击按钮切换下载功能状态

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 修改后需要重启 Edge 浏览器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `kill_edge_process` | L38 | 使用 taskkill 命令强制终止所有 Edge 进程 |
| ⚙️ **函数 (Func)** | `modify_registry` | L68 | 修改或创建 Edge 浏览器的注册表键值。 |
| ⚙️ **函数 (Func)** | `restore_downloads` | L104 | 恢复下载 (设置 DownloadRestrictions = 0) |
| ⚙️ **函数 (Func)** | `disable_downloads` | L108 | 彻底禁用下载 (设置 DownloadRestrictions = 3) |
| ⚙️ **函数 (Func)** | `create_gui` | L113 | 创建并运行 Tkinter GUI 窗口 |

---

## 📄 脚本: [system\Edge-Internet-Control\上网助手.py](./system/Edge-Internet-Control/上网助手.py)

**📖 模块简介**: 小宝工具箱 - 上网助手 (Internet Assistant)

功能：
- 定时控制 Edge 浏览器联网状态
- 支持断网和联网时间设置
- 帮助用户专注工作或学习

使用方法：
- 需要以管理员权限运行
- 设置断网和联网时间
- 点击开始按钮

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 需要安装 pywin32：pip install pywin32

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `执行隐藏命令` | L60 | 替代 os.system，执行命令时不显示黑窗口，也不显示输出结果 |
| ⚙️ **函数 (Func)** | `是否有管理员权限` | L80 | 检测当前程序是否以管理员权限运行 |
| ⚙️ **函数 (Func)** | `智能等待_直到` | L88 | 等待直到某个具体的时间点 |
| ⚙️ **函数 (Func)** | `弹窗提示_非阻塞` | L94 | 在新线程中弹窗，不卡住主程序计时 |
| ⚙️ **函数 (Func)** | `_run` | L96 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `弹窗_3秒自动关闭` | L108 | 最后的弹窗，显示3秒后自动关闭程序 |
| ⚙️ **函数 (Func)** | `禁止_edge_上网` | L131 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `允许_edge_上网` | L147 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `阻断逻辑` | L152 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `居中显示` | L205 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `开始任务并提示` | L216 | 无函数说明文档 |
| ⚙️ **函数 (Func)** | `主界面` | L239 | 无函数说明文档 |

---

## 📄 脚本: [system\Edge-Internet-Control\联网工具.py](./system/Edge-Internet-Control/联网工具.py)

**📖 模块简介**: 小宝工具箱 - Edge 浏览器联网控制工具 (Edge Internet Control)

功能：
- 限制或解除 Edge 浏览器联网权限
- 通过 Windows 防火墙规则控制
- 支持 x86 和 x64 版本的 Edge

使用方法：
- 需要以管理员权限运行
- 点击按钮切换 Edge 的联网状态

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限才能修改防火墙规则
- 修改后需要重启 Edge 浏览器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `is_admin` | L34 | 检查是否具有管理员权限 |
| ⚙️ **函数 (Func)** | `run_as_admin` | L41 | 以管理员权限重新运行当前程序 |
| ⚙️ **函数 (Func)** | `清理规则` | L59 | 执行删除防火墙规则的命令 |
| ⚙️ **函数 (Func)** | `main` | L70 | 无函数说明文档 |

---

## 📄 脚本: [system\Remove-Spotlight-Info\hide_desktop_info.py](./system/Remove-Spotlight-Info/hide_desktop_info.py)

**📖 模块简介**: 小宝工具箱 - 移除桌面了解此图片 (Hide Desktop Info)

功能：
- 移除 Windows 锁屏界面的"了解此图片"按钮
- 通过修改注册表实现
- 让锁屏界面更加简洁

使用方法：
- 直接运行即可移除
- 需要重启资源管理器生效

注意事项：
- 仅支持 Windows 系统
- 需要管理员权限
- 修改后需要重启资源管理器生效

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| ⚙️ **函数 (Func)** | `show_message` | L36 | 显示一个Windows提示框 |
| ⚙️ **函数 (Func)** | `modify_registry` | L41 | 直接修改注册表 |
| ⚙️ **函数 (Func)** | `restart_explorer` | L56 | 重启资源管理器 |
| ⚙️ **函数 (Func)** | `main` | L70 | 无函数说明文档 |

---

## 📄 脚本: [system\startup_manager.py](./system/startup_manager.py)

**📖 模块简介**: 开机启动项管理工具 (Startup Manager)

功能：
- 查看所有开机启动项
- 启用/禁用启动项
- 添加新的启动项
- 删除启动项
- 查看启动项详情

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `StartupManager` | L27 | 开机启动项管理器 |
| 🔹 *方法 (Method)* | `StartupManager.__init__` | L30 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `StartupManager.create_widgets` | L62 | 创建界面组件 |
| 🔹 *方法 (Method)* | `StartupManager.load_startup_items` | L127 | 加载启动项 |
| 🔹 *方法 (Method)* | `StartupManager.on_select` | L160 | 选择启动项 |
| 🔹 *方法 (Method)* | `StartupManager.add_startup_item` | L185 | 添加启动项 |
| 🔹 *方法 (Method)* | `StartupManager.browse_command` | L223 | 浏览命令 |
| 🔹 *方法 (Method)* | `StartupManager.confirm_add` | L232 | 确认添加 |
| 🔹 *方法 (Method)* | `StartupManager.delete_selected` | L267 | 删除选中启动项 |
| 🔹 *方法 (Method)* | `StartupManager.open_startup_folder` | L307 | 打开启动文件夹 |

---

## 📄 脚本: [system\system_cleanup.py](./system/system_cleanup.py)

**📖 模块简介**: 系统垃圾清理工具 (System Cleanup Tool)

功能：
- 清理临时文件
- 清理回收站
- 清理浏览器缓存
- 清理系统日志
- 清理Windows更新缓存

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `SystemCleanupTool` | L29 | 系统垃圾清理工具 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.__init__` | L32 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.create_widgets` | L60 | 创建界面组件 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.format_size` | L138 | 格式化文件大小 |
| 🔹 *方法 (Method)* | `SystemCleanupTool._scan_directory_size` | L146 | 通用目录大小扫描 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_temp_files` | L164 | 扫描临时文件 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_recycle_bin` | L182 | 扫描回收站 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_browser_cache` | L195 | 扫描浏览器缓存 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_system_logs` | L214 | 扫描系统日志 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_update_cache` | L231 | 扫描Windows更新缓存 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_thumbnails` | L236 | 扫描缩略图缓存 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.start_scan` | L256 | 开始扫描 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.scan_worker` | L269 | 扫描工作线程 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.update_scan_result` | L295 | 更新扫描结果 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_selected` | L304 | 清理选中项目 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_all` | L326 | 清理所有项目 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_by_type` | L338 | 根据类型清理 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_temp_files` | L353 | 清理临时文件 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_recycle_bin` | L376 | 清空回收站 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_browser_cache` | L383 | 清理浏览器缓存 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_system_logs` | L399 | 清理系统日志 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_update_cache` | L415 | 清理Windows更新缓存 |
| 🔹 *方法 (Method)* | `SystemCleanupTool.cleanup_thumbnails` | L428 | 清理缩略图缓存 |

---

## 📄 脚本: [vision\gesture_recognizer.py](./vision/gesture_recognizer.py)

**📖 模块简介**: 小宝工具箱 - 手势识别 (Gesture Recognizer)

功能：
- 基于 OpenCV 和 MediaPipe 的手势识别
- 识别手部关键点
- 触发特定 Windows 系统快捷操作

使用方法：
- 直接运行即可启动摄像头
- 使用手势控制屏幕上的角色
- 按 Escape 键退出

注意事项：
- 需要安装 opencv-python：pip install opencv-python
- 需要安装 mediapipe：pip install mediapipe
- 需要摄像头设备

作者：小宝科技站 (xbkjz.cn)
日期：2024


> ⚠️ *该脚本中未检测到显式的类或函数定义，可能为纯顺序流脚本。*

---

## 📄 脚本: [vision\hand_tracking.py](./vision/hand_tracking.py)

**📖 模块简介**: 小宝工具箱 - 手部跟踪 (Hand Tracking)

功能：
- 实时检测摄像头画面中的手部
- 识别手部 21 个关键点
- 实时输出三维坐标

使用方法：
- 直接运行即可启动摄像头
- 按 Escape 键退出

注意事项：
- 需要安装 opencv-python：pip install opencv-python
- 需要安装 mediapipe：pip install mediapipe
- 需要摄像头设备

作者：小宝科技站 (xbkjz.cn)
日期：2024


> ⚠️ *该脚本中未检测到显式的类或函数定义，可能为纯顺序流脚本。*

---

## 📄 脚本: [vision\image_compressor.py](./vision/image_compressor.py)

**📖 模块简介**: 图片批量压缩工具 (Image Batch Compressor)

功能：
- 批量压缩图片
- 支持多种图片格式
- 自定义压缩质量
- 保持原始尺寸或调整尺寸
- 预览压缩效果

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `ImageCompressor` | L29 | 图片批量压缩器 |
| 🔹 *方法 (Method)* | `ImageCompressor.__init__` | L32 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ImageCompressor.create_widgets` | L44 | 创建界面组件 |
| 🔹 *方法 (Method)* | `ImageCompressor.update_quality_label` | L162 | 更新质量标签 |
| 🔹 *方法 (Method)* | `ImageCompressor.toggle_resize` | L166 | 切换调整尺寸选项 |
| 🔹 *方法 (Method)* | `ImageCompressor.add_files` | L175 | 添加文件 |
| 🔹 *方法 (Method)* | `ImageCompressor.add_directory` | L198 | 添加目录 |
| 🔹 *方法 (Method)* | `ImageCompressor.clear_files` | L221 | 清空文件列表 |
| 🔹 *方法 (Method)* | `ImageCompressor.browse_output` | L228 | 浏览输出目录 |
| 🔹 *方法 (Method)* | `ImageCompressor.format_size` | L234 | 格式化文件大小 |
| 🔹 *方法 (Method)* | `ImageCompressor.preview_compression` | L242 | 预览压缩效果 |
| 🔹 *方法 (Method)* | `ImageCompressor.start_compression` | L296 | 开始压缩 |
| 🔹 *方法 (Method)* | `ImageCompressor.compress_worker` | L315 | 压缩工作线程 |
| 🔹 *方法 (Method)* | `ImageCompressor.update_status` | L380 | 更新状态 |
| 🔹 *方法 (Method)* | `ImageCompressor.update_file_status` | L384 | 更新文件状态 |
| 🔹 *方法 (Method)* | `ImageCompressor.open_output_dir` | L398 | 打开输出目录 |
| ⚙️ **函数 (Func)** | `main` | L413 | 主函数 |

---

## 📄 脚本: [vision\screen_capture.py](./vision/screen_capture.py)

**📖 模块简介**: 屏幕截图工具 (Screen Capture Tool)

功能：
- 全屏截图
- 区域截图
- 窗口截图
- 延时截图
- 自动保存

作者：小宝科技站 (xbkjz.cn)
日期：2024


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `ScreenCaptureTool` | L28 | 屏幕截图工具 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.__init__` | L31 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.create_widgets` | L54 | 创建界面组件 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.update_quality_label` | L170 | 更新质量标签 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.browse_dir` | L174 | 浏览目录 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.get_filename` | L181 | 生成文件名 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.save_image` | L188 | 保存图片 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.full_screen_capture` | L209 | 全屏截图 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.region_capture` | L225 | 区域截图 — 使用 Canvas 覆盖全屏实现区域选择 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.on_mouse_down` | L266 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.on_mouse_drag` | L272 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.on_mouse_up` | L281 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.on_escape` | L301 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.window_capture` | L311 | 窗口截图 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.delay_capture` | L337 | 延时截图 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.open_file` | L367 | 打开文件 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.open_dir` | L380 | 打开目录 |
| 🔹 *方法 (Method)* | `ScreenCaptureTool.clear_recent` | L387 | 清空最近列表 |

---

## 📄 脚本: [vision\video_frame_extractor.py](./vision/video_frame_extractor.py)

**📖 模块简介**: 小宝工具箱 - 批量视频截图提取器 (Video Frame Extractor)
功能：一键载入本地任意格式视频（MP4/MKV/AVI等），支持配置等时间步长（例如每 5 秒提取一张）全自动无损批量导出高清截图；
     同时提供预览滑块，支持手动单张截取精准画面帧。截图自动归档保存于专属目录下。
受众：影视解说自媒体人、影视创作者、写电影剧透解析的内容博主、计算机视觉数据集采集人员。


| 节点类型 | 名称 | 所在行数 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| 🏫 **类 (Class)** | `VideoExtractorApp` | L26 | 无类说明文档 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.__init__` | L27 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.setup_ui` | L42 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.select_video` | L110 | 无函数说明文档 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.on_slider_move` | L134 | 当用户拖动滑块时，估算时间点并显示 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.start_extraction` | L148 | 核心批量提取控制器 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.run_batch_extraction` | L176 | 子线程运行的批量提取核心循环 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.grab_single_frame` | L231 | 精准提取滑块选定的一帧并保存 |
| 🔹 *方法 (Method)* | `VideoExtractorApp.reset_buttons` | L259 | 无函数说明文档 |

---
