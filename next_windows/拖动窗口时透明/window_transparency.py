import ctypes
import time
import threading

# Windows API 常量
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002
user32 = ctypes.windll.user32


class WindowTransparency:
    """极简窗口透明度控制器 - 修复版"""

    def __init__(self, target_alpha: int = 180, restore_alpha: int = 255, interval: float = 0.004):
        self.target_alpha = max(0, min(255, target_alpha))
        self.restore_alpha = max(0, min(255, restore_alpha))
        self.interval = max(0.001, interval)
        self._stop_flag = threading.Event()
        self._anim_thread = None

    def _ensure_layered(self, hwnd: int):
        """确保窗口拥有分层属性，并处理初次设置的闪烁问题"""
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not (ex_style & WS_EX_LAYERED):
            # 关键修复：在开启分层属性前，先通过 API 设定一个初始值
            # 否则系统可能默认透明度为 0
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
            user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
            return True  # 标记这是新设置的窗口
        return False

    def _animate(self, hwnd: int, target: int, start: int):
        diff = target - start
        if diff == 0:
            return

        # 优化动画：如果差距过大，加大步长以提升响应速度，或保持平滑
        step = 1 if diff > 0 else -1
        for alpha in range(start + step, target + step, step):
            if self._stop_flag.is_set():
                break
            user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
            time.sleep(self.interval)

    def _start_anim(self, hwnd: int, target: int, current: int):
        # 终止旧动画
        self._stop_flag.set()
        if self._anim_thread and self._anim_thread.is_alive():
            # 这里不用 join 阻塞主线程，防止拖动卡顿
            # 通过 stop_flag 让旧线程自己退出
            pass

        self._stop_flag.clear()
        self._anim_thread = threading.Thread(
            target=self._animate, args=(hwnd, target, current), daemon=True)
        self._anim_thread.start()

    def set_transparent(self, hwnd: int, alpha: int = None):
        """设置窗口透明（带动画）"""
        target = alpha if alpha is not None else self.target_alpha
        target = max(0, min(255, target))

        # 1. 确保分层属性存在
        is_new = self._ensure_layered(hwnd)

        # 2. 获取当前透明度
        current = ctypes.c_ubyte(255)
        # 如果获取失败（比如新窗口），则假定它是 255
        if not user32.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(current), None):
            current.value = 255

        # 3. 如果是新应用拖动，强制初始值为 255，防止从 0 开始闪烁
        start_val = 255 if is_new else current.value

        self._start_anim(hwnd, target, start_val)

    def restore(self, hwnd: int):
        """恢复窗口不透明"""
        self.set_transparent(hwnd, self.restore_alpha)


def if_transparent(hwnd: int) -> bool:
    """判断窗口是否处于透明状态"""
    alpha = ctypes.c_ubyte(255)
    # 如果 API 调用失败，说明窗口根本没设置过透明度，返回 False
    if not user32.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(alpha), None):
        return False
    return alpha.value < 254  # 留一点余量判断
