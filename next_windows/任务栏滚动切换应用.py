import ctypes
from ctypes import wintypes
from pynput.keyboard import Key, Controller

# 强制开启 DPI 感知，确保高分屏下坐标检测准确
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

user32 = ctypes.windll.user32
keyboard = Controller()


class WinEngine:
    def __init__(self):
        self.alt_pressed = False

    def get_taskbar_rect(self):
        """获取任务栏精确坐标"""
        h_taskbar = user32.FindWindowW("Shell_TrayWnd", None)
        rect = wintypes.RECT()
        user32.GetWindowRect(h_taskbar, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def is_mouse_on_taskbar(self, x, y):
        """位置判定"""
        l, t, r, b = self.get_taskbar_rect()
        return l <= x <= r and t <= y <= b

    def stop_switching(self):
        """释放 Alt 键 (用于 Alt+Tab 模式确认选择)"""
        if self.alt_pressed:
            keyboard.release(Key.alt)
            self.alt_pressed = False

    def switch_standard(self, reverse=False):
        """Alt + Tab 模式: 需要按住 Alt 维持界面"""
        if not self.alt_pressed:
            keyboard.press(Key.alt)
            self.alt_pressed = True

        if reverse:
            with keyboard.pressed(Key.shift):
                keyboard.tap(Key.tab)
        else:
            keyboard.tap(Key.tab)

    def switch_persistent(self, reverse=False):
        """Ctrl + Win + Alt + Tab 模式: 界面持久化驻留"""
        with keyboard.pressed(Key.ctrl, Key.cmd, Key.alt):
            if reverse:
                with keyboard.pressed(Key.shift):
                    keyboard.tap(Key.tab)
            else:
                keyboard.tap(Key.tab)
