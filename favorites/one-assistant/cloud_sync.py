# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - 云端白名单开机静默同步任务管理
"""

import os
import sys
import subprocess

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from config import (
    RESOURCE_DIR,
    CLOUD_SYNC_TASK_NAME,
    AUTO_SHUTDOWN_TASK_NAME,
    CLOUD_SYNC_SCRIPT_FILENAME,
    CLOUD_SYNC_DEPLOY_DIR,
    CLOUD_SYNC_SCRIPT_PATH,
    SYNC_SCRIPT_CONTENT
)

def get_cloud_sync_installed():
    if not os.path.exists(CLOUD_SYNC_SCRIPT_PATH):
        return False
    try:
        res = subprocess.run(
            ["schtasks", "/query", "/tn", CLOUD_SYNC_TASK_NAME],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return res.returncode == 0
    except Exception:
        return False

def deploy_sync_script():
    try:
        os.makedirs(CLOUD_SYNC_DEPLOY_DIR, exist_ok=True)
        src = os.path.join(RESOURCE_DIR, CLOUD_SYNC_SCRIPT_FILENAME)
        content = ""
        if os.path.exists(src):
            try:
                with open(src, "r", encoding="utf-8-sig") as f:
                    content = f.read()
            except Exception:
                pass
        if not content:
            content = SYNC_SCRIPT_CONTENT
        with open(CLOUD_SYNC_SCRIPT_PATH, "w", encoding="utf-8-sig") as f:
            f.write(content)
        return True
    except Exception:
        return False

def install_cloud_sync_task():
    if not deploy_sync_script():
        return False, "部署同步脚本到系统目录失败。"
    cmd = [
        "schtasks", "/create",
        "/tn", CLOUD_SYNC_TASK_NAME,
        "/tr", f'powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "{CLOUD_SYNC_SCRIPT_PATH}"',
        "/sc", "onstart",
        "/ru", "SYSTEM",
        "/f"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode == 0:
            run_cloud_sync_now()
            return True, "开机静默云端同步任务已成功部署！\n\n- 运行机制：开机自动以最高 SYSTEM 权限在后台静默运行\n- 浏览器管控：自动同步最新白名单并加锁 Edge/Chrome\n- 晚间纪律：自动部署每日 20:15 定时关机策略\n- 权限特性：彻底免 UAC 弹窗、无黑框界面、普通学生无权修改\n- 同步源：https://xbkjz.cn/edu/whitelist.txt\n\n学生机每次开机将自动静默同步最新白名单并确保关机任务生效！"
        else:
            err = res.stderr.strip() or res.stdout.strip()
            return False, f"创建计划任务失败：{err}"
    except Exception as e:
        return False, f"执行异常：{e}"

def uninstall_cloud_sync_task():
    try:
        res = subprocess.run(
            ["schtasks", "/delete", "/tn", CLOUD_SYNC_TASK_NAME, "/f"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # 同步清理关联的晚间定时关机计划任务
        subprocess.run(
            ["schtasks", "/delete", "/tn", AUTO_SHUTDOWN_TASK_NAME, "/f"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if res.returncode == 0:
            return True, "已成功移除开机云端同步及晚间自动关机任务。"
        else:
            return False, f"移除任务失败：{res.stderr.strip() or res.stdout.strip()}"
    except Exception as e:
        return False, f"执行异常：{e}"

def run_cloud_sync_now():
    if not os.path.exists(CLOUD_SYNC_SCRIPT_PATH):
        deploy_sync_script()
    try:
        subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", CLOUD_SYNC_SCRIPT_PATH],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True, "云端同步执行完成，白名单已刷新。"
    except Exception as e:
        return False, f"同步执行失败：{e}"
