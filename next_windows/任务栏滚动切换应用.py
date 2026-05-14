import ctypes
from ctypes import wintypes
from pynput.keyboard import Key, Controller
from pynput import mouse
import time

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

user32 = ctypes.windll.user32
keyboard = Controller()


class TaskbarScroll:
    def __init__(self, sensitivity=1):
        self.sensitivity = sensitivity
        self.scroll_count = 0
        self.last_time = 0
        self.listener = None

    def __enter__(self):
        # with 启动时
        self.listener = mouse.Listener(
            on_scroll=self._on_scroll,
            on_move=self._on_move
        )
        self.listener.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # with 结束时自动清理
        keyboard.release(Key.alt)
        self.listener.stop()

    def get_taskbar_rect(self):
        h = user32.FindWindowW("Shell_TrayWnd", None)
        rect = wintypes.RECT()
        user32.GetWindowRect(h, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def is_on_taskbar(self, x, y):
        l, t, r, b = self.get_taskbar_rect()
        return l <= x <= r and t <= y <= b

    def _on_move(self, x, y):
        if not self.is_on_taskbar(x, y):
            keyboard.release(Key.alt)

    def _on_scroll(self, x, y, dx, dy):
        if not self.is_on_taskbar(x, y):
            keyboard.release(Key.alt)
            return

        self.scroll_count += int(dy)
        if abs(self.scroll_count) >= self.sensitivity:
            now = time.time()
            if now - self.last_time < 0.01:
                return
            self.last_time = now
            reverse = self.scroll_count > 0
            self.scroll_count = 0
            self.on_scroll(reverse)  # 交给你自定义！

    # ====================== 你自由实现的方法 ======================
    def on_scroll(self, reverse):
        pass
