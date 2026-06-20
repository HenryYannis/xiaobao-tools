#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 海龟时钟 (Turtle Clock)

功能：
- 使用 Python Turtle 绘制的模拟时钟
- 实时显示当前时间
- 精美的表盘设计

使用方法：
- 直接运行即可看到时钟
- 关闭窗口退出

注意事项：
- 需要 turtle 库（Python 自带）
- 需要图形界面支持

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import turtle
from time import localtime, strftime

# 创建主 turtle 对象用于绘制表盘和刻度
t = turtle.Turtle()
t.hideturtle()
t.speed(0)
t.penup()
t.goto(0, -100)
t.pendown()
t.width(5)
t.circle(100)
t.penup()
t.goto(0, 0)
t.width(3)

for x in range(12):
    t.forward(70)
    t.pendown()
    t.forward(30)
    t.penup()
    t.back(100)
    t.right(30)

# 创建第二个 turtle 对象用于显示时间
t2 = turtle.Turtle()
t2.hideturtle()
t2.speed(0)
t2.penup()
t2.goto(-20, -150)

# 定义更新时间和指针的函数
def update_time():
    global tt
    tt = strftime('%I:%M:%S', localtime())
    t2.clear()
    t2.write(tt)
    update_clock_hands()
    turtle.ontimer(update_time, 1000)

# 定义更新时钟指针的函数
def update_clock_hands():
    current_time = localtime()
    hour = current_time.tm_hour % 12
    minute = current_time.tm_min
    second = current_time.tm_sec

    # 秒针
    second_angle = (second / 60) * 360
    t3.clear()
    t3.seth(90 - second_angle)
    t3.pendown()
    t3.forward(80)
    t3.penup()
    t3.backward(80)

    # 分针
    minute_angle = ((minute + second / 60) / 60) * 360
    t4.clear()
    t4.seth(90 - minute_angle)
    t4.pensize(3)
    t4.pendown()
    t4.forward(60)
    t4.penup()
    t4.backward(60)

    # 时针
    hour_angle = ((hour + minute / 60 + second / 3600) / 12) * 360
    t5.clear()
    t5.seth(90 - hour_angle)
    t5.pensize(6)
    t5.pendown()
    t5.forward(40)
    t5.penup()
    t5.backward(40)

# 创建三个 turtle 对象分别用于绘制时针、分针和秒针
t3 = turtle.Turtle()
t3.hideturtle()
t3.speed(0)
t3.penup()
t3.goto(0, 0)

t4 = turtle.Turtle()
t4.hideturtle()
t4.speed(0)
t4.penup()
t4.goto(0, 0)

t5 = turtle.Turtle()
t5.hideturtle()
t5.speed(0)
t5.penup()
t5.goto(0, 0)

tt = strftime('%I:%M:%S', localtime())
t2.write(tt)

update_time()

turtle.done()