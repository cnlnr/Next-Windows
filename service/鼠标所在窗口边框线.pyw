import time
from next_windows.鼠标所在窗口边框线 import *

current_hwnd = 0
DEFAULT_COLOR = 0xFFFFFFFF  # 恢复系统默认


while True:
    new_hwnd = get_target_hwnd()
    target_color = get_accent_color()  # 可以把函数删掉改成你喜欢的颜色

    # 情况 1：鼠标在窗口上
    if new_hwnd != 0:
        # 如果从旧窗口移到新窗口，先还原旧的
        if current_hwnd and new_hwnd != current_hwnd:
            set_border_color(current_hwnd, DEFAULT_COLOR)

        # 检查当前颜色，如果不是主题色（说明被软件重绘覆盖了），则重新应用
        if get_current_border_color(new_hwnd) != target_color:
            set_border_color(new_hwnd, target_color)

        current_hwnd = new_hwnd
        time.sleep(0.05)  # 高频检测，对抗重绘

    # 情况 2：鼠标在空白处
    else:
        if current_hwnd:
            set_border_color(current_hwnd, DEFAULT_COLOR)
            current_hwnd = 0
        time.sleep(0.1)
