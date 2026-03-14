from next_windows.窗口区域扩展.taskbar_scroll import listen_taskbar_scroll
from next_windows.窗口区域扩展 import move_all

# ------------------- 配置 -------------------
MAX_RIGHT_EDGE = 3000      # 最右窗口的左上角x不能 > 这个值（实际为左移极限）
MIN_LEFT_EDGE  = -3000     # 最左窗口的左上角x不能 < 这个值（实际为右移极限）
step = 5                   # 过度动画步长
PIXELS_PER_SCROLL = 400    # 滚轮一次（delta=1）的总移动像素
# ------------------------------------------------

total_offset = 0           # 从程序启动开始的累计右移量（像素）

for delta in listen_taskbar_scroll():
    if delta == 0:
        continue

    move_this_time = delta * PIXELS_PER_SCROLL
    new_offset = total_offset + move_this_time

    # offset 变大 → 窗口向左移 → 撞左边墙
    if new_offset > MAX_RIGHT_EDGE:
        print("左侧已达极限")
        continue

    # offset 变小 → 窗口向右移 → 撞右边墙
    if new_offset < MIN_LEFT_EDGE:
        print("右侧已达极限")
        continue
    for i in range(step):
        move_all.move(move_this_time // step)
    total_offset = new_offset