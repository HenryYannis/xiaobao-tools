# Hosts 域名屏蔽工具

一键通过修改 Windows hosts 文件屏蔽 `xbyxz.cn` 及其主域名相关地址，适合机房、家庭等需要限制访问的场景。与 [Hosts 一键初始化](../Hosts-Reset) 配套使用：屏蔽后可用初始化工具恢复。

## 功能特性
- 一键向 hosts 写入屏蔽规则（`xbyxz.cn`、`www.xbyxz.cn`），已存在时不重复写入。
- 修改后自动执行 `ipconfig /flushdns` 刷新 DNS 缓存。
- 未以管理员身份运行时自动请求提权。

## 使用要求
- 仅支持 Windows 系统。
- 需要管理员权限（程序会自动请求提权）。
- 只追加屏蔽规则，不会删除 hosts 中原有内容；解除屏蔽请使用 [Hosts 一键初始化](../Hosts-Reset)，或手动删除对应规则。

## 使用方式

```bash
python hosts_block.py
```

运行后点击「一键屏蔽」，看到「屏蔽成功」提示即生效。

## 打包命令

```bash
python -m PyInstaller --onefile --windowed --uac-admin --name "一键屏蔽游戏" hosts_block.py
```

成品在 `dist\一键屏蔽游戏.exe`。
