# 文件名: taskbar_swiper.py
import ctypes
from ctypes import wintypes
from pynput.keyboard import Key, Controller
from pynput import mouse

# 设置 DPI 感知，确保高分屏下的任务栏坐标识别准确
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

user32 = ctypes.windll.user32


class TaskbarScroll:
    def __init__(self):
        self.listener = None
        # 统一的键盘控制器与 Alt 状态锁
        self.kb = Controller()
        self.alt_pressed = False

    def __enter__(self):
        self.listener = mouse.Listener(
            on_scroll=self._on_scroll,
            on_move=self._on_move
        )
        self.listener.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_alt()
        if self.listener:
            self.listener.stop()

    def get_taskbar_rect(self):
        """获取 Windows 任务栏的矩形坐标"""
        h = user32.FindWindowW("Shell_TrayWnd", None)
        rect = wintypes.RECT()
        user32.GetWindowRect(h, ctypes.byref(rect))
        return rect.left, rect.top, rect.right, rect.bottom

    def is_on_taskbar(self, x, y):
        """判断鼠标当前是否在任务栏内"""
        l, t, r, b = self.get_taskbar_rect()
        return l <= x <= r and t <= y <= b

    def press_alt(self):
        """安全按下 Alt 键"""
        if not self.alt_pressed:
            self.kb.press(Key.alt)
            self.alt_pressed = True

    def release_alt(self):
        """安全释放 Alt 键"""
        if self.alt_pressed:
            self.kb.release(Key.alt)
            self.alt_pressed = False

    def _on_move(self, x, y):
        # 鼠标一旦离开任务栏，立刻释放 Alt 键
        if not self.is_on_taskbar(x, y):
            self.release_alt()

    def _on_scroll(self, x, y, dx, dy):
        # 滚动时如果鼠标不在任务栏，释放 Alt 并拦截
        if not self.is_on_taskbar(x, y):
            self.release_alt()
            return

        # 只要滚轮动了（dy 不为 0），就立刻触发
        if dy != 0:
            reverse = dy > 0
            self.on_scroll(reverse)

    def on_scroll(self, reverse):
        """留给子类实现的虚方法"""
        pass
