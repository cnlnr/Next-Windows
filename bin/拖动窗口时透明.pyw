from next_windows.拖动窗口时透明.window_transparency import WindowTransparency, is_not_transparent
from next_windows.拖动窗口时透明.wait_for_move_event import wait_for_move_event

controller = None
last_restored_hwnd = None  # 记录我们刚刚恢复完的窗口

while True:
    print("Waiting for move/resize event...")
    is_start, hwnd = wait_for_move_event()

    if is_start:
        # 刚刚被我们恢复的窗口，允许再次拖动（不跳过）
        if hwnd == last_restored_hwnd:
            pass
        # 只有真正原本就透明、且不是我们恢复的窗口，才跳过
        elif not is_not_transparent(hwnd):
            print(f"[跳过] 窗口原本已是透明状态 HWND={hwnd}")
            continue

        if controller:
            controller.restore_transparent()
        controller = WindowTransparency(hwnd, 200, 255, 0.003)
        controller.set_transparent()
        last_restored_hwnd = None

    else:
        if controller:
            controller.restore_transparent()
            last_restored_hwnd = controller.hwnd  # 标记：这是我们刚恢复的
            controller = None