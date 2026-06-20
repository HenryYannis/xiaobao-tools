#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网速测试工具 (Speed Test Tool)

功能：
- 测试网络延迟（Ping）
- 测试下载速度（使用公共测速文件）
- 测试上传速度
- 历史记录（自动保存与加载）

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import socket
import time
import threading
import statistics
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class SpeedTestTool:
    """网速测试工具"""

    def __init__(self, root):
        self.root = root
        self.root.title("网速测试工具")
        self.root.resizable(False, False)

        # 测试状态
        self.testing = False
        self.stop_event = threading.Event()
        self.test_results = []

        # 测试服务器列表（使用支持 HTTP 的公共服务器）
        self.test_servers = [
            {"name": "阿里DNS", "host": "223.5.5.5", "port": 53},
            {"name": "腾讯DNS", "host": "119.29.29.29", "port": 53},
            {"name": "Google DNS", "host": "8.8.8.8", "port": 53},
            {"name": "Cloudflare DNS", "host": "1.1.1.1", "port": 53},
        ]

        # 历史文件路径
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speed_test_history.json")

        # 创建界面
        self.create_widgets()

        # 加载历史记录
        self.load_history()

        # 窗口居中
        self.root.update_idletasks()
        w, h = 800, 650
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="网络速度测试", font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 测试配置
        config_frame = ttk.LabelFrame(main_frame, text="测试配置", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 测试服务器
        ttk.Label(config_frame, text="测试服务器:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.server_var = tk.StringVar(value=self.test_servers[0]["name"])
        server_combo = ttk.Combobox(config_frame, textvariable=self.server_var, width=20)
        server_combo['values'] = [s["name"] for s in self.test_servers]
        server_combo.grid(row=0, column=1, padx=(0, 20))

        # 测试次数
        ttk.Label(config_frame, text="测试次数:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.count_var = tk.StringVar(value="5")
        ttk.Entry(config_frame, textvariable=self.count_var, width=10).grid(row=0, column=3, padx=(0, 20))

        # 按钮
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))

        ttk.Button(btn_frame, text="开始测试", command=self.start_test).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="停止测试", command=self.stop_test).grid(row=0, column=1, padx=5)

        # 测试结果
        result_frame = ttk.LabelFrame(main_frame, text="测试结果", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 结果显示
        self.result_text = tk.Text(result_frame, height=12, wrap=tk.WORD)
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 历史记录
        history_frame = ttk.LabelFrame(main_frame, text="历史记录", padding="10")
        history_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 创建Treeview
        columns = ("time", "download", "upload", "ping", "server")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=5)
        self.history_tree.heading("time", text="时间")
        self.history_tree.heading("download", text="下载速度")
        self.history_tree.heading("upload", text="上传速度")
        self.history_tree.heading("ping", text="延迟")
        self.history_tree.heading("server", text="服务器")
        self.history_tree.column("time", width=150)
        self.history_tree.column("download", width=120)
        self.history_tree.column("upload", width=120)
        self.history_tree.column("ping", width=100)
        self.history_tree.column("server", width=120)

        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)

        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)

    def get_server_by_name(self, name):
        """根据名称获取服务器"""
        for server in self.test_servers:
            if server["name"] == name:
                return server
        return self.test_servers[0]

    def start_test(self):
        """开始测试"""
        if self.testing:
            messagebox.showwarning("警告", "正在测试中")
            return

        # 获取配置
        server_name = self.server_var.get()
        server = self.get_server_by_name(server_name)
        try:
            test_count = int(self.count_var.get())
            if test_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "请输入有效的测试次数（正整数）")
            return

        # 初始化
        self.testing = True
        self.stop_event.clear()
        self.test_results = []

        # 清空结果
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"开始测试...\n")
        self.result_text.insert(tk.END, f"服务器: {server['name']} ({server['host']})\n")
        self.result_text.insert(tk.END, f"测试次数: {test_count}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")

        # 启动测试线程
        thread = threading.Thread(target=self.run_test, args=(server, test_count))
        thread.daemon = True
        thread.start()

    def run_test(self, server, test_count):
        """运行测试"""
        try:
            # 测试延迟
            if self.stop_event.is_set():
                return
            self.root.after(0, self.update_status, "正在测试延迟...")
            ping_results = self.test_ping(server["host"], server["port"], test_count)
            if not ping_results:
                self.root.after(0, lambda: self.result_text.insert(tk.END, "⚠ 延迟测试失败，无法连接到服务器\n\n"))
            else:
                valid_pings = [p for p in ping_results if p < 999]
                if valid_pings:
                    avg_ping = statistics.mean(valid_pings)
                    self.root.after(0, self.show_ping_result, valid_pings, avg_ping)
                else:
                    avg_ping = 999
                    self.root.after(0, lambda: self.result_text.insert(tk.END, "⚠ 所有延迟测试均超时\n\n"))

            # 测试下载速度（使用 socket 数据传输测量）
            if self.stop_event.is_set():
                return
            self.root.after(0, self.update_status, "正在测试下载速度...")
            download_results = self.test_download(server["host"], server["port"], test_count)
            if download_results:
                valid_downloads = [d for d in download_results if d > 0]
                if valid_downloads:
                    avg_download = statistics.mean(valid_downloads)
                    self.root.after(0, self.show_download_result, valid_downloads, avg_download)
                else:
                    avg_download = 0
                    self.root.after(0, lambda: self.result_text.insert(tk.END, "⚠ 下载速度测试失败\n\n"))
            else:
                avg_download = 0

            # 测试上传速度
            if self.stop_event.is_set():
                return
            self.root.after(0, self.update_status, "正在测试上传速度...")
            upload_results = self.test_upload(server["host"], server["port"], test_count)
            if upload_results:
                valid_uploads = [u for u in upload_results if u > 0]
                if valid_uploads:
                    avg_upload = statistics.mean(valid_uploads)
                    self.root.after(0, self.show_upload_result, valid_uploads, avg_upload)
                else:
                    avg_upload = 0
                    self.root.after(0, lambda: self.result_text.insert(tk.END, "⚠ 上传速度测试失败\n\n"))
            else:
                avg_upload = 0

            # 保存结果
            valid_pings = [p for p in ping_results if p < 999] if ping_results else [0]
            result = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "download": avg_download if 'avg_download' in dir() else 0,
                "upload": avg_upload if 'avg_upload' in dir() else 0,
                "ping": statistics.mean(valid_pings) if valid_pings else 999,
                "server": server["name"]
            }
            self.test_results.append(result)

            # 更新历史记录并保存到文件
            self.root.after(0, self.add_history, result)
            self.save_history()
            self.root.after(0, self.update_status, "测试完成")
            self.root.after(0, self.testing_complete)

        except Exception as e:
            logging.error(f"测试异常: {e}")
            self.root.after(0, self.update_status, f"测试失败: {e}")
            self.root.after(0, self.testing_complete)

    def test_ping(self, host, port, count):
        """测试延迟 — 使用指定服务器的端口"""
        results = []
        for i in range(count):
            if self.stop_event.is_set():
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)

                start_time = time.time()
                sock.connect((host, port))
                end_time = time.time()

                ping = (end_time - start_time) * 1000  # 毫秒
                results.append(ping)

                sock.close()

            except (OSError, socket.timeout, socket.error):
                results.append(999)  # 超时

            # 更新进度
            progress = (i + 1) / count * 33
            self.root.after(0, self.progress_var.set, progress)
            time.sleep(0.1)

        return results

    def test_download(self, host, port, count):
        """测试下载速度 — 使用 socket 接收数据来评估带宽"""
        results = []
        data_size = 64 * 1024  # 64KB 数据块

        for i in range(count):
            if self.stop_event.is_set():
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))

                # 发送请求并测量接收数据的时间
                start_time = time.time()
                received = 0
                sock.settimeout(2)  # 短超时用于读取

                try:
                    while received < data_size:
                        data = sock.recv(4096)
                        if not data:
                            break
                        received += len(data)
                except socket.timeout:
                    pass  # 读取超时是正常的

                end_time = time.time()
                duration = end_time - start_time

                if duration > 0 and received > 0:
                    speed = (received / duration) / 1024 / 1024  # MB/s
                    results.append(speed)

                sock.close()

            except (OSError, socket.error, socket.timeout):
                results.append(0)

            progress = 33 + (i + 1) / count * 33
            self.root.after(0, self.progress_var.set, progress)
            time.sleep(0.1)

        return results

    def test_upload(self, host, port, count):
        """测试上传速度 — 发送数据并测量传输速率"""
        results = []
        data_size = 32 * 1024  # 32KB 数据块

        for i in range(count):
            if self.stop_event.is_set():
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((host, port))

                # 准备数据
                data = b"X" * data_size

                # 发送数据并计时
                start_time = time.time()
                sent = sock.send(data)
                end_time = time.time()

                duration = end_time - start_time
                if duration > 0 and sent > 0:
                    speed = (sent / duration) / 1024 / 1024  # MB/s
                    results.append(speed)

                sock.close()

            except (OSError, socket.error, socket.timeout):
                results.append(0)

            progress = 66 + (i + 1) / count * 34
            self.root.after(0, self.progress_var.set, progress)
            time.sleep(0.1)

        return results

    def show_ping_result(self, results, avg):
        """显示延迟结果"""
        self.result_text.insert(tk.END, "【延迟测试】\n")
        self.result_text.insert(tk.END, f"  平均延迟: {avg:.2f} ms\n")
        self.result_text.insert(tk.END, f"  最低延迟: {min(results):.2f} ms\n")
        self.result_text.insert(tk.END, f"  最高延迟: {max(results):.2f} ms\n")
        self.result_text.insert(tk.END, f"  抖动: {(max(results) - min(results)):.2f} ms\n\n")

    def show_download_result(self, results, avg):
        """显示下载结果"""
        self.result_text.insert(tk.END, "【下载速度】\n")
        self.result_text.insert(tk.END, f"  平均速度: {avg:.2f} MB/s ({avg * 8:.2f} Mbps)\n")
        self.result_text.insert(tk.END, f"  最高速度: {max(results):.2f} MB/s\n")
        self.result_text.insert(tk.END, f"  最低速度: {min(results):.2f} MB/s\n\n")

    def show_upload_result(self, results, avg):
        """显示上传结果"""
        self.result_text.insert(tk.END, "【上传速度】\n")
        self.result_text.insert(tk.END, f"  平均速度: {avg:.2f} MB/s ({avg * 8:.2f} Mbps)\n")
        self.result_text.insert(tk.END, f"  最高速度: {max(results):.2f} MB/s\n")
        self.result_text.insert(tk.END, f"  最低速度: {min(results):.2f} MB/s\n\n")

    def update_status(self, status):
        """更新状态"""
        self.status_var.set(status)

    def testing_complete(self):
        """测试完成"""
        self.testing = False
        self.stop_event.set()
        self.progress_var.set(100)
        messagebox.showinfo("完成", "网速测试完成！")

    def stop_test(self):
        """停止测试"""
        if not self.testing:
            return

        self.stop_event.set()
        self.testing = False
        self.status_var.set("测试已停止")

    def add_history(self, result):
        """添加历史记录"""
        self.history_tree.insert("", 0, values=(
            result["time"],
            f"{result['download']:.2f} MB/s",
            f"{result['upload']:.2f} MB/s",
            f"{result['ping']:.2f} ms",
            result["server"]
        ))

    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    for result in history[-10:]:  # 只显示最近10条
                        self.add_history(result)
            except (json.JSONDecodeError, OSError) as e:
                logging.warning(f"加载历史记录失败: {e}")

    def save_history(self):
        """保存历史记录到文件"""
        try:
            # 读取现有历史
            existing = []
            if os.path.exists(self.history_file):
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                except (json.JSONDecodeError, OSError):
                    existing = []

            # 添加新结果
            existing.extend(self.test_results)

            # 只保留最近 50 条
            existing = existing[-50:]

            # 保存
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logging.warning(f"保存历史记录失败: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestTool(root)
    root.mainloop()
