# -*- coding: utf-8 -*-
"""
机房教学策略配置工具 - 白名单规则管理
"""

import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from config import _SCRIPT_DIR, WHITELIST_FILENAME, DEFAULT_ALLOWLIST

def get_whitelist_filepath():
    return os.path.join(_SCRIPT_DIR, WHITELIST_FILENAME)

def load_whitelist():
    filepath = get_whitelist_filepath()
    if not os.path.exists(filepath):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# 机房教学策略配置 - 浏览器允许访问的网址白名单\n")
                f.write("\n".join(DEFAULT_ALLOWLIST) + "\n")
        except Exception:
            pass
        return list(DEFAULT_ALLOWLIST)
    
    rules = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append(line)
    except Exception:
        return list(DEFAULT_ALLOWLIST)
    return rules if rules else list(DEFAULT_ALLOWLIST)

def save_whitelist(rules):
    filepath = get_whitelist_filepath()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# 机房教学策略配置 - 浏览器允许访问的网址白名单\n")
            for r in rules:
                r = r.strip()
                if r:
                    f.write(r + "\n")
        return True
    except Exception:
        return False
