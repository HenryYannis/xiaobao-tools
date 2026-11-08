# Hosts 一键初始化工具

机房电脑 hosts 被改坏、又不方便手工编辑时，双击运行即可恢复为 Windows 默认内容，并自动刷新 DNS 缓存。

## 功能特性
- 一键将系统 hosts 恢复为 Windows 默认内容。
- 修改后自动执行 `ipconfig /flushdns` 刷新 DNS 缓存。
- 内置当前 hosts 预览，重置前可确认文件内容。

## 使用要求
- 仅支持 Windows 系统。
- 需要管理员权限（程序会自动请求提权）。
- 重置会直接覆盖当前 hosts（不备份），请确认没有需要保留的自定义映射。

## 使用方式
1. 双击运行「Hosts初始化.exe」。
2. 确认预览内容后，点击「一键初始化 Hosts」。

源码运行：

```bash
python hosts_reset.py
```

## 打包命令

```bash
python -m PyInstaller --noconfirm --onefile --windowed --name "Hosts初始化" hosts_reset.py
```

成品在 `dist\Hosts初始化.exe`。
