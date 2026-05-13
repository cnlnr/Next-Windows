import ctypes
from ctypes import wintypes
from pynput.keyboard import Key, Controller
from pynput import mouse
import time

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


class NextSwitcher:
    def __init__(self, mode="persistent", sensitivity=1):
        """
        :param mode: "persistent" 或 "standard"
        :param sensitivity: 整数，滚轮滚动的物理格数触发阈值
        """
        self.engine = WinEngine()
        self.mode = mode
        self.sensitivity = sensitivity  # 纯整数逻辑
        self.last_time = 0
        self.scroll_count = 0

    def on_scroll(self, x, y, dx, dy):
        # 1. 区域过滤
        if not self.engine.is_mouse_on_taskbar(x, y):
            if self.mode == "standard":
                self.engine.stop_switching()  # 离开即确认窗口
            return

        # 2. 整数格判定
        self.scroll_count += int(dy)
        if abs(self.scroll_count) >= self.sensitivity:
            # 基础防抖，确保按键模拟不会产生堆栈
            current_time = time.time()
            if current_time - self.last_time < 0.01:
                return

            is_rev = self.scroll_count > 0  # 向上滚为正，对应 Shift+Tab

            if self.mode == "persistent":
                self.engine.switch_persistent(reverse=is_rev)
            else:
                self.engine.switch_standard(reverse=is_rev)

            self.scroll_count = 0  # 达到阈值后清零重计
            self.last_time = current_time

    def on_move(self, x, y):
        # 实时检测，如果鼠标离开任务栏区域，自动完成窗口选择 [cite: 2, 4]
        if self.mode == "standard":
            if not self.engine.is_mouse_on_taskbar(x, y):
                self.engine.stop_switching()

    def run(self):
        # 同时监听鼠标滚动和移动 [cite: 4]
        with mouse.Listener(on_scroll=self.on_scroll, on_move=self.on_move) as listener:
            listener.join()
