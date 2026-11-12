# Win 服务优化工具

图形化管理 7 个常见高内存 / 后台占用 Windows 服务的启动状态（支持一键禁用推荐项、单项设为禁用/手动/自动，以及一键恢复）。

## 功能特性
- 实时读取 7 个服务的注册表启动类型与当前运行状态（与系统语言无关）。
- 支持单项设置为「禁用」「手动」「自动」，并支持一键禁用安全推荐项（`DiagTrack` / `DoSvc` / `RemoteRegistry`）及一键恢复全部为自动。
- 针对受 `LaunchProtected` 保护而 `sc config` 返回「拒绝访问」的服务（如 `DoSvc`），在管理员权限下自动回退为直接修改注册表 `Start` 值（修改后重启生效）。

## 包含服务与注意事项

| 服务名 | 显示名称 | 说明 | 默认推荐关闭 |
| :--- | :--- | :--- | :---: |
| `SysMain` | SysMain (Superfetch) | 内存预加载加速；系统盘为 SSD 时可关，**系统盘为机械硬盘勿关**（外置移动机械硬盘不受影响） | — |
| `DiagTrack` | 连接用户体验和遥测 | 微软遥测数据收集，空闲时可能占用较多 CPU | ✅ |
| `DoSvc` | Delivery Optimization 传递优化 | 系统更新 P2P 传递服务，建议关闭；受系统保护，修改后需重启生效 | ✅ |
| `WSearch` | Windows Search 搜索索引 | 后台建立文件索引，禁用后开始菜单搜索会变慢 | — |
| `Spooler` | Print Spooler 打印服务 | 打印队列服务；无打印机可关，**需要浏览器 `Ctrl+P` 转存 PDF 或使用虚拟打印请保留** | — |
| `WbioSrvc` | Windows 生物识别 | 指纹/人脸登录服务，关闭后仅能使用密码/PIN 登录 | — |
| `RemoteRegistry` | Remote Registry 远程注册表 | 允许远程修改注册表，存在安全隐患，建议关闭 | ✅ |

## 使用要求
- 仅支持 Windows 系统（依赖 `tkinter`、内置 `sc.exe` 与 `winreg`，无需额外第三方库）。
- 需要管理员权限（以管理员身份运行源码，或通过下方 `--uac-admin` 打包后双击自动提权）。

## 运行与打包

源码运行：

```bash
python win_service_optimizer.py
```

打包为单文件 GUI 程序（含自动 UAC 提权清单）：

```bash
python -m PyInstaller --noconfirm --onefile --windowed --uac-admin --name win_service_optimizer win_service_optimizer.py
```

成品位于 `dist\win_service_optimizer.exe`。
