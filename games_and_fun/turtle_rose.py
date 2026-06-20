#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 海龟玫瑰花 (Turtle Rose)

功能：
- 使用 Python Turtle 绘制精美的玫瑰花
- 三维立体效果
- 动画绘制过程

使用方法：
- 直接运行即可观看绘制过程
- 关闭窗口退出

注意事项：
- 需要 turtle 库（Python 自带）
- 需要图形界面支持
- 代码来源于网络，仅供学习交流

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

# 导入 turtle 库
import turtle

#设置初始位置
turtle.penup()
turtle.left(90)
turtle.fd(200)
turtle.pendown()
turtle.right(90)

#先画花蕊
turtle.fillcolor("red")
turtle.begin_fill()
turtle.circle(10,180)
turtle.circle(25,110)
turtle.left(50)
turtle.circle(60,45)
turtle.circle(20,170)
turtle.right(24)
turtle.fd(30)
turtle.left(10)
turtle.circle(30,110)
turtle.fd(20)
turtle.left(40)
turtle.circle(90,70)
turtle.circle(30,150)
turtle.right(30)
turtle.fd(15)
turtle.circle(80,90)
turtle.left(15)
turtle.fd(45)
turtle.right(165)
turtle.fd(20)
turtle.left(155)
turtle.circle(150,80)
turtle.left(50)
turtle.circle(150,90)
turtle.end_fill()

#花瓣 1
turtle.left(150)
turtle.circle(-90,70)
turtle.left(20)
turtle.circle(75,105)
turtle.setheading(60)
turtle.circle(80,98)
turtle.circle(-90,40)

#花瓣 2
turtle.left(180)
turtle.circle(90,40)
turtle.circle(-80,98)
turtle.setheading(-83)

#叶子 1
turtle.fd(30)
turtle.left(90)
turtle.fd(25)
turtle.left(45)
turtle.fillcolor("green")
turtle.begin_fill()
turtle.circle(-80,90)
turtle.right(90)
turtle.circle(-80,90)
turtle.end_fill()
turtle.right(135)
turtle.fd(60)
turtle.left(180)
turtle.fd(85)
turtle.left(90)
turtle.fd(80)

#叶子 2
turtle.right(90)
turtle.right(45)
turtle.fillcolor("green")
turtle.begin_fill()
turtle.circle(80,90)
turtle.left(90)
turtle.circle(80,90)
turtle.end_fill()
turtle.left(135)
turtle.fd(60)
turtle.left(180)
turtle.fd(60)
turtle.right(90)
turtle.circle(200,60)
turtle.done()


if __name__ == "__main__":
    pass
