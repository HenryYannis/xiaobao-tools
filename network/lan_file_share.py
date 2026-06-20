#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 局域网极速文件共享器 (LAN File Share Server)
功能：一键将电脑上的指定目录化身局域网文件共享中心，局域网内的任何手机、平板、电脑只需输入网页地址，
     即可免流量、极速下载电脑上的文件，甚至支持直接在手机浏览器中向电脑上传文件。
受众：教育工作者、教师（一键分发课件）、日常跨平台（手机到电脑）临时传输大文件的办公人员。

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import re
import sys
import socket
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# 终端彩色输出
COLOR_GREEN = "\033[92m"
COLOR_RESET = "\033[0m"

# 安全：允许的文件名字符（字母、数字、中文、常见符号）
SAFE_FILENAME_PATTERN = re.compile(r'^[\w\u4e00-\u9fff.\-()（）\[\]【】\s]+$')


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器，在标准 SimpleHTTPRequestHandler 上提供文件上传能力"""

    # 类级别共享的访问令牌，由 LANShareApp 设置
    access_token = ""

    def do_POST(self):
        """处理局域网内其他设备上传文件的 POST 请求"""
        # 验证访问令牌
        if self.access_token and not self._verify_token():
            self.send_error(403, "Access Denied: Invalid or missing token")
            return

        try:
            # 解析 multipart/form-data 类型的 POST 请求
            boundary = self.headers.get_boundary()
            if not boundary:
                self.send_error(400, "Missing boundary in Content-Type")
                return
            boundary = boundary.encode()
            remainbytes = int(self.headers['content-length'])
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary not in line:
                self.send_error(400, "Content NOT begun with boundary")
                return

            # 读取文件头，提取文件名
            line = self.rfile.readline()
            remainbytes -= len(line)
            fn_index = line.find(b'filename=')
            if fn_index == -1:
                self.send_error(400, "Can't find out file name")
                return

            raw_filename = line[fn_index + 10: -2].decode('utf-8').strip('"')
            # 安全：提取纯文件名并校验
            filename = os.path.basename(raw_filename)
            if not filename or not SAFE_FILENAME_PATTERN.match(filename):
                self.send_error(400, "Invalid filename. Only alphanumeric, Chinese, and common symbols are allowed.")
                return

            # 安全：防止隐藏文件和路径穿越
            if filename.startswith('.') or '..' in filename:
                self.send_error(400, "Hidden files or path traversal not allowed")
                return

            # 读取后续空行
            line = self.rfile.readline()
            remainbytes -= len(line)
            line = self.rfile.readline()
            remainbytes -= len(line)

            # 安全：限制上传文件大小 (500MB)
            MAX_UPLOAD_SIZE = 500 * 1024 * 1024
            if remainbytes > MAX_UPLOAD_SIZE:
                self.send_error(413, "File too large. Maximum upload size is 500MB.")
                return

            # 写入本地文件
            out_filepath = os.path.join(self.directory, filename)
            try:
                out = open(out_filepath, 'wb')
            except (IOError, PermissionError) as e:
                logging.warning(f"无法创建文件 {out_filepath}: {e}")
                self.send_error(403, "Can't create file to write, permission denied.")
                return

            # 循环写入文件体
            preline = self.rfile.readline()
            remainbytes -= len(preline)
            while remainbytes > 0:
                line = self.rfile.readline()
                remainbytes -= len(line)
                if boundary in line:
                    preline = preline[0:-1]
                    if preline.endswith(b'\r'):
                        preline = preline[0:-1]
                    out.write(preline)
                    out.close()
                    logging.info(f"文件上传成功: {filename}")
                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    # 返回上传成功的精致反馈页面
                    # 安全：对 filename 做 HTML 转义防 XSS
                    safe_name = filename.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                    response_html = f"""
                    <html>
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            body {{ font-family: -apple-system, sans-serif; text-align: center; padding: 40px; background-color: #f5f5f7; }}
                            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: inline-block; max-width: 320px; }}
                            h2 {{ color: #34c759; }}
                            a {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #007aff; color: white; text-decoration: none; border-radius: 6px; }}
                        </style>
                    </head>
                    <body>
                        <div class="card">
                            <h2>✓ 上传成功！</h2>
                            <p>文件 <b>{safe_name}</b> 已成功存入分享电脑！</p>
                            <a href="/">返回主页</a>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(response_html.encode('utf-8'))
                    return
                else:
                    out.write(preline)
                    preline = line

            out.close()
            self.send_error(400, "Unexpected end of file")
        except Exception as e:
            logging.error(f"上传处理异常: {e}")
            self.send_error(500, f"Internal error: {e}")

    def list_directory(self, path):
        """重写目录列表生成方法，在页面顶部注入一个精致的文件上传 HTML 表单"""
        # 验证访问令牌（浏览也需验证）
        if self.access_token and not self._verify_token():
            self.send_response(403)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>403 Access Denied</h1><p>Invalid or missing access token.</p></body></html>")
            return None

        try:
            dir_list = os.listdir(path)
        except OSError as e:
            logging.warning(f"无法列出目录 {path}: {e}")
            self.send_error(404, "No permission to list directory")
            return None

        # 页面美化与上传表单注入
        r = []
        displaypath = self.path
        enc = sys.getfilesystemencoding()
        title = f"小宝极速局域网共享器: {displaypath}"

        r.append('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        r.append(f'<html>\n<head>\n<meta name="viewport" content="width=device-width, initial-scale=1">')
        r.append(f'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
        r.append(f'<title>{title}</title>\n')
        r.append("""
        <style>
            body { font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background-color: #f6f8fa; color: #24292f; }
            h2 { color: #0969da; border-bottom: 1px solid #d0d7de; padding-bottom: 8px; }
            .upload-box { background: white; border: 1px dashed #0969da; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
            .file-list { background: white; border: 1px solid #d0d7de; border-radius: 8px; list-style: none; padding: 0; }
            .file-item { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid #d0d7de; }
            .file-item:last-child { border-bottom: none; }
            .file-item a { color: #0969da; text-decoration: none; font-weight: 500; flex-grow: 1; word-break: break-all; }
            .file-item a:hover { text-decoration: underline; }
            .btn { background-color: #2da44e; color: white; border: none; padding: 8px 16px; font-weight: 600; border-radius: 6px; cursor: pointer; }
            .btn:hover { background-color: #2c974b; }
            input[type="file"] { margin: 8px; }
            .size-info { color: #57606a; font-size: 0.85em; margin-left: 10px; }
        </style>
        """)
        r.append('</head>\n<body>')
        r.append(f'<h2>📂 局域网共享目录: {displaypath}</h2>\n')

        # 注入极速上传卡片
        r.append('<div class="upload-box">')
        r.append('<h3>📤 极速上传文件到此目录</h3>')
        r.append('<form ENCTYPE="multipart/form-data" METHOD="POST">')
        r.append('<input NAME="file" TYPE="file"/>')
        r.append('<input class="btn" TYPE="submit" VALUE="开始上传"/>')
        r.append('</form>')
        r.append('</div>')

        # 渲染文件列表
        r.append('<ul class="file-list">')
        # 提供返回上级目录
        if displaypath != "/":
            r.append('<li class="file-item"><a href="..">📁 .. (返回上级目录)</a></li>')

        for name in sorted(dir_list):
            if name.startswith('.'):
                continue
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # 文件夹加 Emoji 图标，并显示文件大小
            if os.path.isdir(fullname):
                displayname = f"📁 {name}/"
                linkname = f"{name}/"
            else:
                try:
                    size = os.path.getsize(fullname)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    displayname = f"📄 {name} <span class='size-info'>({size_str})</span>"
                except OSError:
                    displayname = f"📄 {name}"

            r.append(f'<li class="file-item"><a href="{linkname}">{displayname}</a></li>')

        r.append('</ul>\n<hr>\n</body>\n</html>\n')

        encoded = '\n'.join(r).encode(enc, 'surrogateescape')

        self.send_response(200)
        self.send_header("Content-type", f"text/html; charset={enc}")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)
        return None

    def _verify_token(self):
        """验证请求中的访问令牌"""
        # 从 cookie 或查询参数中获取令牌
        # 首先检查查询参数
        if '?' in self.path:
            query = self.path.split('?', 1)[1]
            if f"token={self.access_token}" in query:
                return True

        # 检查 cookie
        cookie_header = self.headers.get('Cookie', '')
        if f"access_token={self.access_token}" in cookie_header:
            return True

        return False


class LANShareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("小宝局域网极速共享器")
        self.root.resizable(False, False)

        self.server = None
        self.server_thread = None
        self.is_running = False
        self.share_dir = os.path.abspath(os.path.dirname(__file__))
        self.port = 8080
        self.local_ip = self.get_local_ip()

        self.setup_ui()

        # 窗口居中
        self.root.update_idletasks()
        w, h = 480, 535
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    def get_local_ip(self):
        """自动提取电脑所在的局域网真实 IP 地址"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except (OSError, socket.error):
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def setup_ui(self):
        # 头部横幅
        header = tk.Label(self.root, text="🌐 局域网极速文件共享器", font=("Helvetica", 16, "bold"), fg="#0969da")
        header.pack(pady=15)

        # 目录选择区
        dir_frame = tk.LabelFrame(self.root, text="选择需要分享的目录", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        dir_frame.pack(padx=20, fill="x")

        self.dir_path_label = tk.Label(dir_frame, text=self.share_dir, wraplength=380, anchor="w", fg="#24292f")
        self.dir_path_label.pack(side="left", fill="x", expand=True)

        select_btn = tk.Button(dir_frame, text="选择目录", command=self.select_directory, bg="#f6f8fa", relief="groove")
        select_btn.pack(side="right", padx=5)

        # 参数配置区
        param_frame = tk.Frame(self.root)
        param_frame.pack(pady=15)

        tk.Label(param_frame, text="共享端口: ").grid(row=0, column=0, padx=5)
        self.port_entry = tk.Entry(param_frame, width=8, justify="center")
        self.port_entry.insert(0, str(self.port))
        self.port_entry.grid(row=0, column=1, padx=5)

        # 访问令牌
        token_frame = tk.LabelFrame(self.root, text="安全设置（可选）", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        token_frame.pack(padx=20, fill="x")

        tk.Label(token_frame, text="访问令牌:").pack(side="left", padx=5)
        self.token_entry = tk.Entry(token_frame, width=20, show="*")
        self.token_entry.insert(0, "")
        self.token_entry.pack(side="left", padx=5)
        tk.Label(token_frame, text="留空则无需认证", fg="#57606a").pack(side="left", padx=5)

        # 状态控制及指示
        self.status_label = tk.Label(self.root, text="● 已停止共享", font=("Helvetica", 11, "bold"), fg="#cf222e")
        self.status_label.pack(pady=5)

        self.url_text = tk.Text(self.root, height=3, width=50, state="disabled", font=("Courier", 10), bg="#f6f8fa", relief="flat")
        self.url_text.pack(pady=10, padx=20)

        # 核心启动按钮
        self.control_btn = tk.Button(self.root, text="启动共享服务", font=("Helvetica", 12, "bold"), bg="#2da44e", fg="white",
                                     relief="flat", activebackground="#2c974b", command=self.toggle_server)
        self.control_btn.pack(pady=15, ipadx=10, ipady=5)

        # 分割线与底栏
        from tkinter import ttk
        sep = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        sep.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        author_frame = tk.Frame(self.root, pady=4)
        author_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(
            author_frame,
            text="作者：小宝科技站 (",
            font=("微软雅黑", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=(15, 0))

        link_lbl = tk.Label(
            author_frame,
            text="xbkjz.cn",
            font=("微软雅黑", 8, "underline"),
            fg="#0066CC",
            cursor="hand2"
        )
        link_lbl.pack(side=tk.LEFT)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://xbkjz.cn"))
        link_lbl.bind("<Enter>", lambda e: link_lbl.configure(fg="#0044AA"))
        link_lbl.bind("<Leave>", lambda e: link_lbl.configure(fg="#0066CC"))

        tk.Label(
            author_frame,
            text=")",
            font=("微软雅黑", 8),
            fg="gray"
        ).pack(side=tk.LEFT)

    def select_directory(self):
        if self.is_running:
            messagebox.showwarning("警告", "共享服务运行期间无法修改分享目录，请先停止服务。")
            return
        selected = filedialog.askdirectory(initialdir=self.share_dir)
        if selected:
            self.share_dir = os.path.abspath(selected)
            self.dir_path_label.config(text=self.share_dir)

    def start_http_server(self):
        """开启 HTTP 共享服务的线程核心逻辑"""
        dir_to_share = self.share_dir
        access_token = self.token_entry.get().strip()

        class CustomHTTPHandler(CustomHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=dir_to_share, **kwargs)

        # 设置访问令牌
        CustomHTTPHandler.access_token = access_token

        try:
            self.server = TCPServer(("", self.port), CustomHTTPHandler)
            auth_info = " (需令牌认证)" if access_token else ""
            print(f"{COLOR_GREEN}[SUCCESS]{COLOR_RESET} 局域网服务在端口 {self.port} 启动{auth_info}")
            self.server.serve_forever()
        except (OSError, socket.error) as e:
            self.is_running = False
            self.root.after(0, lambda: messagebox.showerror("启动失败", f"无法启动服务端口被占用，错误: {e}"))
            self.root.after(0, self.reset_ui_to_stopped)

    def toggle_server(self):
        if not self.is_running:
            # 获取并验证端口号
            try:
                self.port = int(self.port_entry.get())
                if self.port < 1024 or self.port > 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "端口号必须是 1024 - 65535 之间的整数")
                return

            # 开启共享
            self.is_running = True
            token = self.token_entry.get().strip()
            auth_suffix = f"?token={token}" if token else ""
            self.status_label.config(text=f"● 共享中 (IP: {self.local_ip}:{self.port})", fg="#2da44e")
            self.control_btn.config(text="停止共享服务", bg="#cf222e", activebackground="#a40e26")
            self.port_entry.config(state="disabled")
            self.token_entry.config(state="disabled")

            # 写入状态指示框
            access_url = f"http://{self.local_ip}:{self.port}{auth_suffix}"
            self.url_text.config(state="normal")
            self.url_text.delete(1.0, tk.END)
            if token:
                self.url_text.insert(tk.END, f"局域网设备输入以下网址直接访问:\n{access_url}\n(首次访问需携带令牌参数)")
            else:
                self.url_text.insert(tk.END, f"局域网设备输入以下网址直接访问:\n{access_url}")
            self.url_text.config(state="disabled")

            # 开启后台守护线程，避免卡死 Tkinter UI
            self.server_thread = threading.Thread(target=self.start_http_server)
            self.server_thread.daemon = True
            self.server_thread.start()
        else:
            # 停止共享
            self.is_running = False
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            self.reset_ui_to_stopped()

    def reset_ui_to_stopped(self):
        self.status_label.config(text="● 已停止共享", fg="#cf222e")
        self.control_btn.config(text="启动共享服务", bg="#2da44e", activebackground="#2c974b")
        self.port_entry.config(state="normal")
        self.token_entry.config(state="normal")
        self.url_text.config(state="normal")
        self.url_text.delete(1.0, tk.END)
        self.url_text.config(state="disabled")


if __name__ == "__main__":
    app_root = tk.Tk()
    app = LANShareApp(app_root)

    # 窗口关闭拦截，防端口泄露
    def on_app_closing():
        if app.is_running and app.server:
            app.server.shutdown()
            app.server.server_close()
        app_root.destroy()

    app_root.protocol("WM_DELETE_WINDOW", on_app_closing)
    app_root.mainloop()
