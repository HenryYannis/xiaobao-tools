# System-Restrictions-Tool

系统权限与策略控制中心。这是一个集成了三项实用功能的系统策略管理工具，适合机房管理、公共展示电脑或家长控制环境。

## 功能特性
1. **禁止修改壁纸**：一键锁定/解锁当前桌面壁纸，阻止用户通过个性化设置或右键图片修改。
2. **移除桌面“了解此图片”**：隐藏 Windows 聚焦（Spotlight）在桌面上生成的“了解此图片”图标与右键菜单，使桌面重回极简干净。
3. **禁用浏览器离线小游戏**：通过写入系统注册表组策略，完全禁用 Chrome 恐龙游戏 (Dino) 和 Edge 冲浪游戏 (Surf)。

## 使用要求
- 仅支持 Windows 系统。
- 需要以管理员权限运行。
- 修改壁纸和“了解此图片”需要重启资源管理器生效（本工具支持一键或修改后自动重启资源管理器）。
- 修改浏览器游戏后需要重启浏览器生效。

## 打包命令

使用 `PyInstaller` 将本脚本打包为独立的 `.exe` 可执行文件：

```bash
pyinstaller --onefile --windowed --uac-admin --name="SystemRestrictionsController" system_restrictions_tool.py
```
