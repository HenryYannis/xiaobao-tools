#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口扫描工具 (Port Scanner)

功能：
- 扫描指定IP地址的开放端口
- 支持自定义端口范围
- 支持多线程扫描
- 识别常见服务
- 导出扫描结果

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import socket
import threading
import queue
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class PortScanner:
    """端口扫描器"""

    def __init__(self, root):
        self.root = root
        self.root.title("端口扫描工具")
        self.root.geometry("900x700")

        # 扫描状态
        self.scanning = False
        self.stop_event = threading.Event()
        self.port_queue = queue.Queue()
        self.results = []

        # 常见端口和服务
        self.common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            1521: "Oracle",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            6379: "Redis",
            8080: "HTTP-Proxy",
            8443: "HTTPS-Alt",
            27017: "MongoDB",
        }

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 扫描配置
        config_frame = ttk.LabelFrame(main_frame, text="扫描配置", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 目标IP
        ttk.Label(config_frame, text="目标IP:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.ip_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(config_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, padx=(0, 20))

        # 端口范围
        ttk.Label(config_frame, text="端口范围:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.start_port_var = tk.StringVar(value="1")
        ttk.Entry(config_frame, textvariable=self.start_port_var, width=10).grid(row=0, column=3, padx=(0, 5))
        ttk.Label(config_frame, text="-").grid(row=0, column=4, padx=(0, 5))
        self.end_port_var = tk.StringVar(value="1024")
        ttk.Entry(config_frame, textvariable=self.end_port_var, width=10).grid(row=0, column=5, padx=(0, 20))

        # 线程数
        ttk.Label(config_frame, text="线程数:").grid(row=0, column=6, padx=(0, 5), sticky=tk.W)
        self.thread_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.thread_var, width=10).grid(row=0, column=7)

        # 超时时间
        ttk.Label(config_frame, text="超时(秒):").grid(row=1, column=0, padx=(0, 5), sticky=tk.W, pady=(10, 0))
        self.timeout_var = tk.StringVar(value="1")
        ttk.Entry(config_frame, textvariable=self.timeout_var, width=10).grid(row=1, column=1, padx=(0, 20), pady=(10, 0))

        # 常用端口
        ttk.Label(config_frame, text="常用端口:").grid(row=1, column=2, padx=(0, 5), sticky=tk.W, pady=(10, 0))
        self.common_var = tk.StringVar()
        common_combo = ttk.Combobox(config_frame, textvariable=self.common_var, width=15)
        common_combo['values'] = ["所有常用端口"] + [f"{port} ({service})" for port, service in self.common_ports.items()]
        common_combo.grid(row=1, column=3, columnspan=3, padx=(0, 20), pady=(10, 0))
        common_combo.bind("<<ComboboxSelected>>", self.on_common_port_select)

        # 按钮
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=1, column=6, columnspan=2, pady=(10, 0))

        ttk.Button(btn_frame, text="开始扫描", command=self.start_scan).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="停止扫描", command=self.stop_scan).grid(row=0, column=1, padx=5)

        # 扫描结果
        result_frame = ttk.LabelFrame(main_frame, text="扫描结果", padding="10")
        result_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 创建Treeview
        columns = ("port", "state", "service", "banner")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=20)
        self.tree.heading("port", text="端口")
        self.tree.heading("state", text="状态")
        self.tree.heading("service", text="服务")
        self.tree.heading("banner", text="Banner")
        self.tree.column("port", width=100)
        self.tree.column("state", width=100)
        self.tree.column("service", width=150)
        self.tree.column("banner", width=400)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 统计信息
        stats_frame = ttk.Frame(result_frame)
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.scanned_var = tk.StringVar(value="已扫描: 0")
        ttk.Label(stats_frame, textvariable=self.scanned_var).grid(row=0, column=0, padx=(0, 20))

        self.open_var = tk.StringVar(value="开放端口: 0")
        ttk.Label(stats_frame, textvariable=self.open_var).grid(row=0, column=1, padx=(0, 20))

        self.time_var = tk.StringVar(value="耗时: 0秒")
        ttk.Label(stats_frame, textvariable=self.time_var).grid(row=0, column=2)

        # 按钮
        btn_frame2 = ttk.Frame(main_frame)
        btn_frame2.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        ttk.Button(btn_frame2, text="导出结果", command=self.export_results).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame2, text="清空结果", command=self.clear_results).grid(row=0, column=1, padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

    def on_common_port_select(self, event):
        """选择常用端口"""
        selection = self.common_var.get()
        if selection == "所有常用端口":
            ports = sorted(self.common_ports.keys())
            self.start_port_var.set(str(ports[0]))
            self.end_port_var.set(str(ports[-1]))
        else:
            port = int(selection.split(" ")[0])
            self.start_port_var.set(str(port))
            self.end_port_var.set(str(port))

    def start_scan(self):
        """开始扫描"""
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中")
            return

        # 获取配置
        target = self.ip_var.get()
        try:
            start_port = int(self.start_port_var.get())
            end_port = int(self.end_port_var.get())
            threads = int(self.thread_var.get())
            timeout = float(self.timeout_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        if start_port > end_port:
            messagebox.showerror("错误", "起始端口不能大于结束端口")
            return

        # 清空结果
        self.clear_results()

        # 初始化
        self.scanning = True
        self.stop_event.clear()
        self.results = []
        self.total_ports = end_port - start_port + 1
        self.scanned_count = 0
        self.open_count = 0

        # 添加端口到队列
        for port in range(start_port, end_port + 1):
            self.port_queue.put(port)

        # 更新状态
        self.status_var.set(f"正在扫描 {target}...")
        self.start_time = time.time()

        # 启动工作线程
        for _ in range(min(threads, self.total_ports)):
            thread = threading.Thread(target=self.scan_worker, args=(target, timeout))
            thread.daemon = True
            thread.start()

        # 启动进度更新
        self.update_progress()

    def scan_worker(self, target, timeout):
        """扫描工作线程"""
        while not self.stop_event.is_set():
            try:
                port = self.port_queue.get_nowait()
            except queue.Empty:
                break

            try:
                # 创建socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)

                # 尝试连接
                result = sock.connect_ex((target, port))

                if result == 0:
                    # 端口开放
                    service = self.common_ports.get(port, "未知")
                    banner = self.get_banner(sock, target, port)

                    self.results.append({
                        "port": port,
                        "state": "开放",
                        "service": service,
                        "banner": banner
                    })

                    # 更新UI
                    self.root.after(0, self.add_result, port, "开放", service, banner)
                    self.open_count += 1

                sock.close()

            except (OSError, socket.error) as e:
                logging.debug(f"扫描端口 {port} 失败: {e}")

            self.scanned_count += 1
            self.port_queue.task_done()

    def get_banner(self, sock, target, port):
        """获取Banner"""
        try:
            # 发送HTTP请求
            if port in [80, 8080, 8443]:
                sock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
            else:
                sock.send(b"\r\n")

            # 接收响应
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            return banner[:100] if banner else ""
        except (OSError, socket.error, socket.timeout):
            return ""

    def update_progress(self):
        """更新进度"""
        if not self.scanning:
            return

        # 更新进度条
        progress = (self.scanned_count / self.total_ports) * 100
        self.progress_var.set(progress)

        # 更新统计
        self.scanned_var.set(f"已扫描: {self.scanned_count}")
        self.open_var.set(f"开放端口: {self.open_count}")

        # 计算耗时
        elapsed = time.time() - self.start_time
        self.time_var.set(f"耗时: {elapsed:.1f}秒")

        # 检查是否完成
        if self.scanned_count >= self.total_ports:
            self.scanning = False
            self.status_var.set(f"扫描完成，发现 {self.open_count} 个开放端口")
            messagebox.showinfo("完成", f"扫描完成，发现 {self.open_count} 个开放端口")
        else:
            self.root.after(100, self.update_progress)

    def stop_scan(self):
        """停止扫描"""
        if not self.scanning:
            return

        self.stop_event.set()
        self.scanning = False
        self.status_var.set("扫描已停止")

    def add_result(self, port, state, service, banner):
        """添加结果"""
        self.tree.insert("", tk.END, values=(port, state, service, banner))

    def clear_results(self):
        """清空结果"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results = []
        self.scanned_var.set("已扫描: 0")
        self.open_var.set("开放端口: 0")
        self.time_var.set("耗时: 0秒")
        self.progress_var.set(0)

    def export_results(self):
        """导出结果"""
        if not self.results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return

        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="导出结果",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("文本文件", "*.txt")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["端口", "状态", "服务", "Banner"])
                for result in self.results:
                    writer.writerow([result["port"], result["state"], result["service"], result["banner"]])

            self.status_var.set(f"结果已导出到: {file_path}")
            messagebox.showinfo("成功", f"结果已导出到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PortScanner(root)
    root.mainloop()
