from next_windows.拖动窗口时透明.window_transparency import WindowTransparency, if_transparent
from next_windows.拖动窗口时透明.wait_for_move_event import wait_for_move_event

controller = WindowTransparency(target_alpha=200, restore_alpha=255, interval=0.003)
active_hwnd = None
last_restored_hwnd = None

while True:
    print("Waiting for move/resize event...")
    is_start, hwnd = wait_for_move_event()

    if is_start:
        # 刚刚恢复的窗口，允许再次拖动
        if hwnd == last_restored_hwnd:
            pass
        elif if_transparent(hwnd):
            print(f"[跳过] 窗口原本已是透明状态 HWND={hwnd}")
            continue

        # 恢复之前正在控制的窗口
        if active_hwnd and active_hwnd != hwnd:
            controller.restore(active_hwnd)
        
        print(f"[START] HWND={hwnd} 设置透明")
        controller.set_transparent(hwnd)
        active_hwnd = hwnd
        last_restored_hwnd = None

    else:
        # 拖动结束
        if active_hwnd:
            print(f"[END] HWND={active_hwnd} 恢复")
            controller.restore(active_hwnd)
            last_restored_hwnd = active_hwnd
            active_hwnd = None