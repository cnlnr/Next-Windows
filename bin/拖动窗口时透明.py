from next_windows.拖动窗口时透明.window_transparency import WindowTransparency, is_not_transparent
from next_windows.拖动窗口时透明.wait_for_move_event import wait_for_move_event

controller = None

while True:
    print("Waiting for move/resize event...")
    is_start, hwnd = wait_for_move_event()

    if is_start:
        if is_not_transparent(hwnd):
            continue
        print(f"[START] HWND={hwnd}")
        controller = WindowTransparency(hwnd, 200, 255, 0.003)
        controller.set_transparent()
    elif controller:
        print(f"[END] 恢复透明度")
        controller.restore_transparent()
        controller = None


