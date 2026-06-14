@echo off
chcp 65001 >nul
echo ===================================================
echo 正在安装打包依赖项 (PyInstaller ^& pywin32)...
python -m pip install pyinstaller pywin32
echo ===================================================
echo 正在将 上网助手.py 打包为 msedge_helper.exe...
echo [注意] 已启用 --noconsole，确保双击运行时不会闪现任何黑色控制台窗口。
rem 提取版本信息代码段生成纯文本供 PyInstaller 使用
echo 正在解析版本元数据...
powershell -Command "$content = Get-Content 'VERSION_INFO.md' -Raw; if ($content -match '(?s)```\r?\n(.*?)\r?\n```') { $Matches[1] | Set-Content 'version.txt' -Encoding utf8 }"

if exist "图标.ico" (
    python -m PyInstaller --noconsole --onefile --version-file=version.txt --icon=图标.ico --name=msedge_helper 上网助手.py
) else if exist "edge.ico" (
    python -m PyInstaller --noconsole --onefile --version-file=version.txt --icon=edge.ico --name=msedge_helper 上网助手.py
) else (
    python -m PyInstaller --noconsole --onefile --version-file=version.txt --name=msedge_helper 上网助手.py
)
if exist "version.txt" del "version.txt"
echo ===================================================
echo.
echo 打包完成！生成的文件 msedge_helper.exe 位于 dist 文件夹中。
echo.
echo 【如何手动设置开机自启和桌面解锁】：
echo 1. 将 dist 文件夹中的 msedge_helper.exe 复制到您的安装目录下（如 C:\Program Files 或您指定的文件夹）。
echo 2. 在 msedge_helper.exe 上右键，选择 [发送到 - 桌面快捷方式]，并将该桌面快捷方式重命名为 [上网助手]。
echo 3. 按键盘上的 Win + R 键，输入 shell:startup 并回车，这会打开 Windows 的 [启动] 文件夹。
echo 4. 将桌面上的 [上网助手] 快捷方式复制一份，粘贴到这个 [启动] 文件夹中。
echo 5. 在 [启动] 文件夹中的快捷方式上右键选择 [属性]，在 [目标] 输入框的末尾，加上一个空格和参数 --startup。
echo    例如变成: "C:\path\to\msedge_helper.exe" --startup
echo    这样开机时就会以静默模式自动开始后台断网，而学生双击桌面图标会直接弹出解锁密码框。
echo.
pause
