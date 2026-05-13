import ctypes
from ctypes import wintypes
from pynput.keyboard import Key, Controller

# 感知 DPI 缩放，确保任务栏坐标检测准确
ctypes.windll.shcore.SetProcessDpiAwareness(1)
user32 = ctypes.windll.user32
keyboard = Controller()


class WinEngine:
    def __init__(self):
        self.alt_pressed = False

    def get_taskbar_rect(self):
        h_taskbar = user32.FindWindowW("Shell_TrayWnd", None)
        rect = wintypes.RECT()
        user32.GetWindowRect(h_taskbar, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def is_mouse_on_taskbar(self, x, y):
        l, t, r, b = self.get_taskbar_rect()
        # 增加 2 像素容错
        return l <= x <= r and t - 2 <= y <= b

    def stop_switching(self):
        """释放所有可能的挂起键"""
        if self.alt_pressed:
            keyboard.release(Key.alt)
            self.alt_pressed = False

    def switch_standard(self, reverse=False):
        """模式1: 传统的 Alt + Tab (瞬时/保持)"""
        if not self.alt_pressed:
            keyboard.press(Key.alt)
            self.alt_pressed = True

        if reverse:
            with keyboard.pressed(Key.shift):
                keyboard.tap(Key.tab)
        else:
            keyboard.tap(Key.tab)

    def switch_persistent(self, reverse=False):
        """模式2: Ctrl + Win + Alt + Tab (持久化界面)"""
        # 这个快捷键在 Windows 中通常不需要按住，按一次即呼出
        with keyboard.pressed(Key.ctrl, Key.cmd, Key.alt):
            if reverse:
                with keyboard.pressed(Key.shift):
                    keyboard.tap(Key.tab)
            else:
                keyboard.tap(Key.tab)
