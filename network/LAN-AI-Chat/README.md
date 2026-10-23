# LAN-AI-Chat

> ⚠️ **源码未公开 / 计划中**：这个目录目前只有说明、图标（`robot.ico`）和版本信息（`VERSION_INFO.md`），客户端源码 `局域网Ai大模型.pyw` 还没有放进仓库，所以下面的打包命令暂时无法直接运行。源码公开后我会更新这里。

一台主机下载安装 Ollama 并配置模型，然后其他电脑运行客户端即可

该模型是定制版，可下载修改代码实现自己定制化需求

## 打包命令

```bash
pyinstaller --onefile --icon="robot.ico" --version-file="版本信息.txt" 局域网Ai大模型.pyw
```

> 注：`--version-file` 需要的版本信息内容在 `VERSION_INFO.md` 的代码块里，打包前请复制出来另存为 `版本信息.txt`。
