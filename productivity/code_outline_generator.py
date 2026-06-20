#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 代码结构大纲生成器 (Code Structure Outline Generator)
功能：一键扫描指定目录下的所有 Python 脚本，使用 AST (抽象语法树) 提取其中的模块、类、函数的结构及对应的文档注释(Docstring)，
     并自动在本地生成一份精美的项目结构大纲 Markdown 文档。
用途：方便开发者快速梳理项目，或将整洁的代码大纲提供给 AI (如 OpenAI Codex/ChatGPT) 进行高效的 Code Review 与测试用例设计。

作者：小宝科技站 (xbkjz.cn)
日期：2026
"""

import os
import ast
import sys
from pathlib import Path

# 终端彩色输出支持
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

if sys.platform.startswith('win'):
    # Windows 终端彩色字体兼容性处理
    os.system('color')

class OutlineParser(ast.NodeVisitor):
    """AST 节点访问器，专门用于提取类、函数以及对应的 Docstring"""
    def __init__(self, filename):
        self.filename = filename
        self.outline = []
        self.current_class = None

    def visit_ClassDef(self, node):
        docstring = ast.get_docstring(node) or "无类说明文档"
        # 提取第一行作为简要说明
        brief = docstring.strip().split('\n')[0]
        self.outline.append({
            "type": "class",
            "name": node.name,
            "brief": brief,
            "line": node.lineno
        })
        # 记录当前在解析类内部的方法
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        docstring = ast.get_docstring(node) or "无函数说明文档"
        brief = docstring.strip().split('\n')[0]
        
        # 判断是普通函数还是类的方法
        func_type = "method" if self.current_class else "function"
        parent = self.current_class if self.current_class else None
        
        self.outline.append({
            "type": func_type,
            "name": node.name,
            "parent": parent,
            "brief": brief,
            "line": node.lineno
        })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """处理 async def 定义的异步函数/方法"""
        docstring = ast.get_docstring(node) or "无异步函数说明文档"
        brief = docstring.strip().split('\n')[0]
        
        # 异步函数判断类型
        func_type = "async_method" if self.current_class else "async_function"
        parent = self.current_class if self.current_class else None
        
        self.outline.append({
            "type": func_type,
            "name": node.name,
            "parent": parent,
            "brief": brief,
            "line": node.lineno
        })
        self.generic_visit(node)

def generate_outline(target_dir, output_file):
    """扫描指定目录下的所有 Python 文件并生成大纲"""
    target_path = Path(target_dir).resolve()
    print(f"{COLOR_BLUE}[INFO]{COLOR_RESET} 开始扫描目录: {COLOR_YELLOW}{target_path}{COLOR_RESET}")
    
    # 忽略的文件及目录列表
    ignored_dirs = {'.git', '.github', '__pycache__', 'venv', '.venv', 'env', '.pytest_cache'}
    
    py_files = []
    for root, dirs, files in os.walk(target_path):
        # 排除忽略的目录
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            if file.endswith('.py') and file != Path(__file__).name:
                py_files.append(Path(root) / file)
                
    if not py_files:
        print(f"{COLOR_RED}[WARNING]{COLOR_RESET} 未在目标目录中找到任何 Python 文件！")
        return

    print(f"{COLOR_BLUE}[INFO]{COLOR_RESET} 检索到 {len(py_files)} 个 Python 脚本文件。开始解析语法树...")
    
    md_content = []
    md_content.append(f"# 🛠 项目代码结构与大纲看板 (Code Outline Board)\n")
    md_content.append(f"> 本文档由 **小宝工具箱 - 代码结构大纲生成器** 自动生成。\n")
    md_content.append(f"> 它可以快速提取代码中所有的类、方法、函数及其 Docstring 注释，方便开发者和 AI 进行结构化感知。\n\n---\n")

    for py_file in sorted(py_files):
        relative_path = py_file.relative_to(target_path)
        print(f" -> 解析中: {COLOR_GREEN}{relative_path}{COLOR_RESET}")
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 使用 AST 解析
            tree = ast.parse(code_content)
            module_docstring = ast.get_docstring(tree) or "无模块整体功能介绍。"
            
            md_content.append(f"## 📄 脚本: [{relative_path}](./{relative_path.as_posix()})\n")
            md_content.append(f"**📖 模块简介**: {module_docstring.strip()}\n\n")
            
            parser = OutlineParser(py_file.name)
            parser.visit(tree)
            
            if not parser.outline:
                md_content.append(f"> ⚠️ *该脚本中未检测到显式的类或函数定义，可能为纯顺序流脚本。*\n\n---\n")
                continue
                
            md_content.append("| 节点类型 | 名称 | 所在行数 | 核心功能简介 |")
            md_content.append("| :--- | :--- | :--- | :--- |")
            
            for item in parser.outline:
                if item["type"] == "class":
                    md_content.append(f"| 🏫 **类 (Class)** | `{item['name']}` | L{item['line']} | {item['brief']} |")
                elif item["type"] == "function":
                    md_content.append(f"| ⚙️ **函数 (Func)** | `{item['name']}` | L{item['line']} | {item['brief']} |")
                elif item["type"] == "method":
                    md_content.append(f"| 🔹 *方法 (Method)* | `{item['parent']}.{item['name']}` | L{item['line']} | {item['brief']} |")
                elif item["type"] == "async_function":
                    md_content.append(f"| ⚡ **异步函数 (Async)** | `{item['name']}` | L{item['line']} | {item['brief']} |")
                elif item["type"] == "async_method":
                    md_content.append(f"| ⚡ *异步方法 (Async)* | `{item['parent']}.{item['name']}` | L{item['line']} | {item['brief']} |")
            
            md_content.append("\n---\n")
            
        except Exception as e:
            print(f"{COLOR_RED}[ERROR]{COLOR_RESET} 解析 {relative_path} 失败，错误: {e}")
            md_content.append(f"## 📄 脚本: {relative_path}\n")
            md_content.append(f"❌ *解析失败，可能包含语法错误或非 UTF-8 编码。*\n\n---\n")

    # 写入大纲文档
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write("\n".join(md_content))
        
    print(f"\n{COLOR_GREEN}[SUCCESS]{COLOR_RESET} 大纲解析大功告成！已成功输出到:")
    print(f" -> {COLOR_YELLOW}{output_path.resolve()}{COLOR_RESET}\n")

if __name__ == "__main__":
    # 默认扫描当前脚本所在的项目根目录（当前路径的上一级或根目录）
    current_dir = Path(__file__).resolve().parents[1]
    output_report = current_dir / "PROJECT_OUTLINE.md"
    
    print("=" * 60)
    print(" 小宝工具箱 - 项目代码结构大纲自动生成器")
    print("=" * 60)
    
    generate_outline(current_dir, output_report)
