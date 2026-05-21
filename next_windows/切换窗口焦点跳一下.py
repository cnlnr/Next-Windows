import ctypes
import time
import threading
from ctypes import wintypes

user32 = ctypes.windll.user32

EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_OUTOFCONTEXT = 0x0000

WinEventProcType = ctypes.WINFUNCTYPE(
    None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
    wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD
)


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("rcNormalPosition", wintypes.RECT),
    ]


def generate_pixel_path(amplitude, step_size, bounce_overshoot, bounce_count):
    offsets = []

    # 确保步长合法，防止死循环
    step_size = max(1, step_size)

    # 1. 冲顶
    curr = 0
    while curr < amplitude:
        curr = min(amplitude, curr + step_size)
        offsets.append(curr)

    # 2. 回落
    while curr > 0:
        curr = max(0, curr - step_size)
        offsets.append(curr)

    # 3. 多级余震回弹
    for i in range(bounce_count):
        decay_factor = i + 1
        current_overshoot = max(1, bounce_overshoot // decay_factor)

        # 回弹下探（负向移动）
        offset = 0
        while offset < current_overshoot:
            offset = min(current_overshoot, offset + step_size)
            offsets.append(-offset)

        # 回弹归位
        while offset > 0:
            offset = max(0, offset - step_size)
            offsets.append(-offset)

    return offsets


def execute_jump(hwnd, amplitude, step_size, step_delay, bounce_overshoot, bounce_count):
    # 确保跳动的是整个顶级大窗体，而不是内部的子控件
    top_hwnd = user32.GetAncestor(hwnd, 2)
    if not top_hwnd:
        top_hwnd = hwnd

    rect = wintypes.RECT()
    if not user32.GetWindowRect(top_hwnd, ctypes.byref(rect)):
        return

    x, y = rect.left, rect.top
    if x < -10000 or y < -10000:
        return

    flags = 0x0001 | 0x0004 | 0x0010 | 0x0020
    offsets = generate_pixel_path(
        amplitude, step_size, bounce_overshoot, bounce_count)

    for offset in offsets:
        user32.SetWindowPos(top_hwnd, 0, x, y - offset, 0, 0, flags)
        if step_delay > 0:
            time.sleep(step_delay)

    user32.SetWindowPos(top_hwnd, 0, x, y, 0, 0, flags)


def process_window_focus(hwnd, amplitude, step_size, step_delay, bounce_overshoot, bounce_count, taskbar_delay, minimize_timeout, check_interval):
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_name, 256)
    if class_name.value in ["Shell_TrayWnd", "Progman", "WorkerW"]:
        return

    wp = WINDOWPLACEMENT()
    wp.length = ctypes.sizeof(WINDOWPLACEMENT)
    user32.GetWindowPlacement(hwnd, ctypes.byref(wp))

    is_from_minimize = user32.IsIconic(hwnd) or (wp.showCmd == 2)

    if is_from_minimize:
        t_start = time.time()
        while time.time() - t_start < minimize_timeout:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if rect.top > -10000:
                break
            time.sleep(check_interval)
        time.sleep(taskbar_delay)

    execute_jump(hwnd, amplitude, step_size, step_delay,
                 bounce_overshoot, bounce_count)


def event_callback_handler(hwnd, amplitude, step_size, step_delay, bounce_overshoot, bounce_count, taskbar_delay, minimize_timeout, check_interval):
    if hwnd:
        threading.Thread(
            target=process_window_focus,
            args=(hwnd, amplitude, step_size, step_delay, bounce_overshoot,
                  bounce_count, taskbar_delay, minimize_timeout, check_interval),
            daemon=True
        ).start()
