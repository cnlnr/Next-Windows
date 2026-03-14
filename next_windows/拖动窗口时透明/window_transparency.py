import ctypes
import time
import threading

# Windows API 常量
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002
user32 = ctypes.windll.user32


class WindowTransparency:
    """
    极简窗口透明度控制器
    功能：设置透明 / 恢复透明（带动画）
    """

    def __init__(self, hwnd: int, target_alpha: int = 180, restore_alpha: int = 255, interval: float = 0.004):
        """
        初始化
        :param hwnd: 窗口句柄
        :param target_alpha: 默认设置的透明度（0-255）
        :param restore_alpha: 恢复时的透明度（默认255不透明）
        :param interval: 动画每步间隔（秒）
        """
        self.hwnd = hwnd
        self.target_alpha = max(0, min(255, target_alpha))  # 限制0-255
        self.restore_alpha = max(0, min(255, restore_alpha))
        self.interval = max(0.001, interval)  # 最小间隔

        # 内部状态
        self._current_alpha = 255
        self._anim_thread = None
        self._stop_flag = threading.Event()

        # 确保窗口支持透明
        self._ensure_layered()

    def _ensure_layered(self):
        """让窗口支持透明效果"""
        ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        if not (ex_style & WS_EX_LAYERED):
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE,
                                  ex_style | WS_EX_LAYERED)

    def _set_alpha(self, alpha: int):
        """立即设置透明度（内部用）"""
        user32.SetLayeredWindowAttributes(self.hwnd, 0, alpha, LWA_ALPHA)
        self._current_alpha = alpha

    def _animate(self, target: int):
        """渐变动画线程"""
        start = self._current_alpha
        diff = target - start
        if diff == 0:
            return

        step = 1 if diff > 0 else -1
        for alpha in range(start + step, target + step, step):
            if self._stop_flag.is_set():
                return
            self._set_alpha(alpha)
            time.sleep(self.interval)
        self._set_alpha(target)

    def _start_anim(self, target: int):
        """安全启动动画（中断旧动画）"""
        self._stop_flag.set()
        if self._anim_thread and self._anim_thread.is_alive():
            self._anim_thread.join()
        self._stop_flag.clear()
        self._anim_thread = threading.Thread(
            target=self._animate, args=(target,), daemon=True)
        self._anim_thread.start()

    # ===================== 你要的公开方法 =====================
    def set_transparent(self, alpha: int = None):
        """
        设置透明（带动画）
        不传入alpha则使用初始化的默认值
        """
        target = alpha if alpha is not None else self.target_alpha
        self._start_anim(max(0, min(255, target)))

    def restore_transparent(self):
        """
        恢复透明（初始化时设定的恢复值）
        """
        self._start_anim(self.restore_alpha)


def is_not_transparent(hwnd: int) -> bool:
    """
    判断窗口是否【不具有透明样式】
    """
    ex_style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, -20)
    return bool(ex_style & 0x00080000)


# ===================== 测试示例 =====================
if __name__ == "__main__":
    import win32gui

    # 找到记事本窗口
    hwnd = win32gui.FindWindow("Notepad", None)
    print(f"记事本窗口是否不具有透明样式: {is_not_transparent(hwnd)}")
    if not hwnd:
        print("未找到记事本，请先打开！")
    else:
        # 初始化：窗口、默认透明150、恢复255、动画速度
        controller = WindowTransparency(
            hwnd, target_alpha=150, restore_alpha=255, interval=0.003)

        print("设置透明...")
        controller.set_transparent()
        time.sleep(1.2)

        print("恢复透明...")
        controller.restore_transparent()
        time.sleep(1)

        print("完成！")
