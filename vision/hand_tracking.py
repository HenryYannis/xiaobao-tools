#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小宝工具箱 - 手部跟踪 (Hand Tracking)

功能：
- 实时检测摄像头画面中的手部
- 识别手部 21 个关键点
- 实时输出三维坐标

使用方法：
- 直接运行即可启动摄像头
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

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        cv2.imshow('Hand Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()


if __name__ == "__main__":
    pass
