from next_windows.拖动窗口时透明.window_transparency import WindowTransparency, is_not_transparent
from next_windows.拖动窗口时透明.wait_for_move_event import wait_for_move_event


while True:
    is_start, hwnd = wait_for_move_event()
    if is_start and is_not_transparent(hwnd):
        controller = WindowTransparency(hwnd, target_alpha=200, interval=0.002)
        controller.set_transparent()
    else:
        try:
            controller.restore_transparent()
        except NameError:
            pass
