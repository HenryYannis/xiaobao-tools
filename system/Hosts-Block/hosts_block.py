# -*- coding: utf-8 -*-
import os
import sys
import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
    sys.exit(0)

def block_hosts():
    if not is_admin():
        run_as_admin()
        return

    try:
        content = ""
        if os.path.exists(HOSTS_PATH):
            import stat
            try:
                os.chmod(HOSTS_PATH, stat.S_IWRITE)
            except Exception:
                pass

            try:
                with open(HOSTS_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(HOSTS_PATH, "r", encoding="gbk", errors="ignore") as f:
                    content = f.read()

        if "xbyxz.cn" not in content:
            rules = "\n\n# Block xbyxz\n127.0.0.1 xbyxz.cn\n127.0.0.1 www.xbyxz.cn\n0.0.0.0 xbyxz.cn\n0.0.0.0 www.xbyxz.cn\n"
            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                f.write(content.rstrip() + rules)

        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        messagebox.showinfo("提示", "屏蔽成功")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("错误", f"屏蔽失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("屏蔽工具")
    root.geometry("300x150")
    root.resizable(False, False)
    root.configure(bg="#F5F7FA")

    # 居中窗口
    root.eval('tk::PlaceWindow . center')

    btn = tk.Button(
        root,
        text="一键屏蔽",
        font=("Microsoft YaHei", 14, "bold"),
        bg="#2563EB",
        fg="#FFFFFF",
        activebackground="#1D4ED8",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        command=block_hosts
    )
    btn.place(relx=0.5, rely=0.5, anchor="center", width=220, height=55)

    root.mainloop()
