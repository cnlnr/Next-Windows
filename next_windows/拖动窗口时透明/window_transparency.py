import ctypes
import time
import threading

# Windows API 常量
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002
user32 = ctypes.windll.user32


class WindowTransparency:
    """极简窗口透明度控制器 - 实例复用版"""

    def __init__(self, target_alpha: int = 180, restore_alpha: int = 255, interval: float = 0.004):
        self.target_alpha = max(0, min(255, target_alpha))
        self.restore_alpha = max(0, min(255, restore_alpha))
        self.interval = max(0.001, interval)
        self._stop_flag = threading.Event()
        self._anim_thread = None

    def _ensure_layered(self, hwnd: int):
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not (ex_style & WS_EX_LAYERED):
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)

    def _animate(self, hwnd: int, target: int, start: int):
        diff = target - start
        if diff == 0:
            return
        step = 1 if diff > 0 else -1
        for alpha in range(start + step, target + step, step):
            if self._stop_flag.is_set():
                return
            user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
            time.sleep(self.interval)

    def _start_anim(self, hwnd: int, target: int, current: int):
        self._stop_flag.set()
        if self._anim_thread and self._anim_thread.is_alive():
            self._anim_thread.join(timeout=0.1)
        self._stop_flag.clear()
        self._anim_thread = threading.Thread(
            target=self._animate, args=(hwnd, target, current), daemon=True)
        self._anim_thread.start()

    def set_transparent(self, hwnd: int, alpha: int = None):
        """设置窗口透明（带动画）"""
        target = alpha if alpha is not None else self.target_alpha
        target = max(0, min(255, target))
        self._ensure_layered(hwnd)
        
        current = ctypes.c_ubyte()
        user32.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(current), None)
        
        self._start_anim(hwnd, target, current.value)

    def restore(self, hwnd: int):
        """恢复窗口不透明"""
        self.set_transparent(hwnd, self.restore_alpha)


def is_not_transparent(hwnd: int) -> bool:
    """判断窗口是否不透明（可用于决定是否变透明）"""
    alpha = ctypes.c_ubyte()
    user32.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(alpha), None)
    return alpha.value == 255


# ===================== 测试示例 =====================
if __name__ == "__main__":
    import win32gui

    # 单个实例控制多个窗口
    ctrl = WindowTransparency(target_alpha=150, interval=0.003)

    # 控制记事本
    notepad = win32gui.FindWindow("Notepad", None)
    if notepad:
        print(is_not_transparent(notepad))
        print("记事本变透明...")
        ctrl.set_transparent(notepad)
        time.sleep(1.2)
        ctrl.restore(notepad)

