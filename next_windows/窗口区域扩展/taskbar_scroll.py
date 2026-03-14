import win32gui
from pynput import mouse
from queue import Queue

TASKBAR_CLASSES = {"Shell_TrayWnd", "SecondaryTrayWnd"}

def is_cursor_on_taskbar():
    try:
        _, _, (x, y) = win32gui.GetCursorInfo()
        hwnd = win32gui.WindowFromPoint((x, y))
        while hwnd:
            if win32gui.GetClassName(hwnd) in TASKBAR_CLASSES:
                return True
            hwnd = win32gui.GetParent(hwnd)
    except:
        pass
    return False

def listen_taskbar_scroll():
    """使用生成器封装，支持 for 循环"""
    event_queue = Queue()

    def _on_scroll(x, y, dx, dy):
        if is_cursor_on_taskbar():
            event_queue.put(dy)

    # 在后台启动监听
    listener = mouse.Listener(on_scroll=_on_scroll)
    listener.start()

    try:
        while True:
            # 从队列中获取事件，这会让 for 循环在没有滚动时“阻塞”等待，不占 CPU
            yield event_queue.get()
    finally:
        listener.stop()
