from next_windows.窗口区域扩展.taskbar_scroll import listen_taskbar_scroll
from next_windows.窗口区域扩展 import move_all

# ------------------- 配置 -------------------
MAX_RIGHT_EDGE = 1000      # 最右窗口的左上角x不能 > 这个值
MIN_LEFT_EDGE  = -1000     # 最左窗口的左上角x不能 < 这个值
STEP_PER_SCROLL = 150      # 滚轮一次移动的像素（可调）
SCROLL_MULTIPLIER = 3      # 滚轮灵敏度（一次滚轮 ≈ 3×STEP）
# ------------------------------------------------

total_offset = 0           # 从程序启动开始的累计右移量（像素）

for delta in listen_taskbar_scroll():
    if delta == 0:
        continue

    move_this_time = delta * STEP_PER_SCROLL * SCROLL_MULTIPLIER
    new_offset = total_offset + move_this_time

    # offset 变大 → 窗口向左移 → 容易撞左侧墙
    if new_offset > MAX_RIGHT_EDGE:          # 这里 MAX_RIGHT_EDGE 实际含义变成了“最大左移允许值”
        print("左侧已达极限")   # ← 按你看到的现象改成这样
        continue

    # offset 变小 → 窗口向右移 → 容易撞右侧墙
    if new_offset < MIN_LEFT_EDGE:
        print("右侧已达极限")
        continue

    move_all.move(move_this_time)
    total_offset = new_offset