# LAN-Word-Learner

局域网联机英语单词记忆与测试工具，支持多人同步，兼顾趣味与学习。

## 打包命令

```bash
pyinstaller --onefile --icon="vs.ico" --version-file="VERSION_INFO.md" --windowed --add-data "words.txt;." word_learner.py
```
