import time
import math
import pyautogui

# Fail-safe triggered by moving mouse to any screen corner
pyautogui.FAILSAFE = True

print("[TACTICAL ALERT] Executing circular cursor sweep protocol, General SSB.")
print("[INFO] Move mouse to any screen corner to abort immediately.")

# Circle parameters
radius = 150
duration = 5.0  # seconds per full revolution
steps = 60      # smoothness points
center_x, center_y = pyautogui.position()

try:
    while True:
        for i in range(steps):
            angle = (i / float(steps)) * 2 * math.pi
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            pyautogui.moveTo(x, y, duration=(duration / steps))
except pyautogui.FailSafeException:
    print("[ABORT] Failsafe triggered. Circular sweep terminated.")
