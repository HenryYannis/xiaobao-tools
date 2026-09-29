# 上网助手 (msedge_helper)

小宝工具箱的上网控制工具，在后台静默运行并强制管理 Edge 浏览器上网时间。

## 运行规则
- **断网区间**：每小时的 `00 ~ 44` 分钟，自动强制结束 Edge 浏览器进程。
- **放行区间**：每小时的 `45 ~ 59` 分钟，允许 Edge 浏览器正常上网。
- **密码临时解锁**：双击运行并输入密码 `Pythoa-Scratci` 可免限制临时上网 90 分钟（基于硬件滴答计时，修改系统时间无效）。
- **设备与网络警告**：WiFi 掉线或插入外置 U 盘时，将弹出真全屏模态强置顶警告屏保。支持在屏保窗口输入密码（`Pythoa-Scratci`）独立关闭全屏遮挡提示（不解锁 Edge 浏览器），拔出 U 盘或连上 WiFi 后也会自动恢复状态。

## 自定义修改
如果需要修改断网或联网的时长区间，请直接修改 [上网助手.py](上网助手.py) 的 `周期检测()` 函数中的 `当前分钟 < 45` 这一判断条件即可。

## 打包命令
如果系统环境变量中包含 PyInstaller，可以直接在当前目录下运行：
```bash
pyinstaller --onefile --windowed --icon="图标.ico" --version-file="版本信息.txt" 上网助手.py
```

如果提示找不到 `pyinstaller` 命令，请使用 Python 模块方式进行打包（更稳妥）：
```bash
python -m PyInstaller --onefile --windowed --icon="图标.ico" --version-file="版本信息.txt" 上网助手.py
```
