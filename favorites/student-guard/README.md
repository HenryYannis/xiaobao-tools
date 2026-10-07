# 学生机纪律守护助手 (Student Guard - msedge_helper)

小宝工具箱的学生机运行看护与纪律工具，在后台静默运行并监控设备与网络状态。

## 运行规则
- **晚间自动关机**：到达预设时间（默认 20:15）自动触发系统关机倒计时（60秒）。
- **WiFi 断网检测警告**：WiFi 掉线或断网时，自动弹出全屏置顶警告界面；网络重新连接后自动恢复。
- **U 盘插入检测警告**：检测到外部 U 盘插入时，自动弹出全屏置顶警告界面；拔出 U 盘后自动恢复。

## 自定义修改
如果需要修改晚间自动关机时间，请直接修改 [上网助手.py](file:///c:/Users/A3/Desktop/xiaobao-tools/favorites/student-guard/%E4%B8%8A%E7%BD%91%E5%8A%A9%E6%89%8B.py) 顶部的常量：
```python
SHUTDOWN_HOUR = 20
SHUTDOWN_MINUTE = 15
```

## 打包命令
如果系统环境变量中包含 PyInstaller，可以直接在当前目录下运行：
```bash
pyinstaller --onefile --windowed --icon="图标.ico" --version-file="版本信息.txt" 上网助手.py
```

如果提示找不到 `pyinstaller` 命令，请使用 Python 模块方式进行打包（更稳妥）：
```bash
python -m PyInstaller --onefile --windowed --icon="图标.ico" --version-file="版本信息.txt" 上网助手.py
```
