import ctypes
import time
import math
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


def execute_jump(hwnd, amplitude, duration):
    """底层物理弹跳过渡"""
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return

    x, y = rect.left, rect.top
    if x < -10000 or y < -10000:
        return

    flags = 0x0001 | 0x0004 | 0x0010 | 0x0020
    steps = 6
    step_delay = duration / steps

    for i in range(steps + 1):
        progress = i / steps
        offset_ratio = math.sin(progress * math.pi)
        current_offset = int(amplitude * offset_ratio)
        user32.SetWindowPos(hwnd, 0, x, y - current_offset, 0, 0, flags)
        time.sleep(step_delay)

    user32.SetWindowPos(hwnd, 0, x, y, 0, 0, flags)


def process_window_focus(hwnd, amplitude, duration, taskbar_delay):
    """底层状态分流"""
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_name, 256)
    if class_name.value in ["Shell_TrayWnd", "Progman", "WorkerW"]:
        return

    wp = WINDOWPLACEMENT()
    wp.length = ctypes.sizeof(WINDOWPLACEMENT)
    user32.GetWindowPlacement(hwnd, ctypes.byref(wp))

    is_from_minimize = user32.IsIconic(hwnd) or (wp.showCmd == 2)

    if is_from_minimize:
        start_time = time.time()
        while time.time() - start_time < 0.4:
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if rect.top > -10000:
                break
            time.sleep(0.01)
        time.sleep(taskbar_delay)

    execute_jump(hwnd, amplitude, duration)


def event_callback_handler(hwnd, amplitude, duration, taskbar_delay):
    """由 main.py 的外壳回调直接导入并触发的多线程句柄"""
    if hwnd:
        threading.Thread(
            target=process_window_focus,
            args=(hwnd, amplitude, duration, taskbar_delay),
            daemon=True
        ).start()
