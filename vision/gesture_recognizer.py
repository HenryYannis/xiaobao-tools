#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 手势识别 (Gesture Recognizer)

功能：
- 基于 OpenCV 和 MediaPipe 的手势识别
- 识别手部关键点
- 触发特定 Windows 系统快捷操作

使用方法：
- 直接运行即可启动摄像头
- 使用手势控制屏幕上的角色
- 按 Escape 键退出

注意事项：
- 需要安装 opencv-python：pip install opencv-python
- 需要安装 mediapipe：pip install mediapipe
- 需要摄像头设备

作者：小宝科技站 (xbkjz.cn)
日期：2024
"""

import cv2
import mediapipe as mp
import numpy as np

# 初始化MediaPipe手部识别模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,  # 只识别一只手，更稳定
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# 角色属性
character_size = 50  # 角色方块大小
character_color = (0, 0, 255)  # 红色 (BGR格式)
character_pos = [320, 240]  # 初始位置（屏幕中央）
character_speed = 0.3  # 角色移动平滑度（0-1之间，越大越灵敏）

# 目标点属性
target_color = (0, 255, 0)  # 绿色
target_size = 15  # 目标点大小
target_pos = [100, 100]  # 初始目标位置
target_speed = [2, 3]  # 目标移动速度

# 得分
score = 0
font = cv2.FONT_HERSHEY_SIMPLEX

# 打开摄像头
cap = cv2.VideoCapture(0)
# 设置摄像头分辨率（可根据你的Y5200F摄像头调整）
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("摄像头已启动，请将手放在摄像头前...")
print("用食指控制红色方块，去吃绿色目标点！")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break
    
    # 水平翻转图像（镜像效果，更符合直觉）
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 识别手部
    results = hands.process(frame_rgb)
    
    # 更新目标位置
    target_pos[0] += target_speed[0]
    target_pos[1] += target_speed[1]
    
    # 目标碰壁反弹
    if target_pos[0] <= target_size or target_pos[0] >= 640 - target_size:
        target_speed[0] = -target_speed[0]
    if target_pos[1] <= target_size or target_pos[1] >= 480 - target_size:
        target_speed[1] = -target_speed[1]
    
    # 如果检测到手
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 获取食指尖（索引8）的坐标
            index_finger_tip = hand_landmarks.landmark[8]
            h, w, _ = frame.shape
            finger_x = int(index_finger_tip.x * w)
            finger_y = int(index_finger_tip.y * h)
            
            # 平滑移动角色（让角色缓慢跟随手指，而不是瞬间跳跃）
            character_pos[0] += (finger_x - character_pos[0]) * character_speed
            character_pos[1] += (finger_y - character_pos[1]) * character_speed
            
            # 绘制手部关键点和连线（可选，用于调试）
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
            
            # 绘制手指指示点（蓝色）
            cv2.circle(frame, (finger_x, finger_y), 8, (255, 0, 0), -1)
    
    # 绘制角色（红色方块）
    char_x = int(character_pos[0])
    char_y = int(character_pos[1])
    cv2.rectangle(frame, 
                  (char_x - character_size//2, char_y - character_size//2),
                  (char_x + character_size//2, char_y + character_size//2),
                  character_color, -1)
    
    # 绘制目标（绿色圆形）
    cv2.circle(frame, 
               (int(target_pos[0]), int(target_pos[1])), 
               target_size, target_color, -1)
    
    # 检测碰撞
    distance = np.sqrt((char_x - target_pos[0])**2 + (char_y - target_pos[1])**2)
    if distance < (character_size//2 + target_size):
        score += 1
        # 重置目标位置
        target_pos = [np.random.randint(50, 590), np.random.randint(50, 430)]
        # 随机改变目标速度
        target_speed = [np.random.randint(-5, 5), np.random.randint(-5, 5)]
        # 确保速度不为0
        if target_speed[0] == 0:
            target_speed[0] = np.random.choice([-3, 3])
        if target_speed[1] == 0:
            target_speed[1] = np.random.choice([-3, 3])
    
    # 显示得分
    cv2.putText(frame, f'Score: {score}', (10, 30), font, 1, (255, 255, 255), 2)
    
    # 显示提示信息
    cv2.putText(frame, 'Move your index finger to control', (10, 460), 
                font, 0.5, (255, 255, 255), 1)
    
    # 显示画面
    cv2.imshow('Hand Tracking Game', frame)
    
    # 按'q'退出
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()


if __name__ == "__main__":
    pass
hands.close()
