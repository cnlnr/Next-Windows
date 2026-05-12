import ctypes
import time
import threading
from typing import Dict

# Windows API 常量
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002
user32 = ctypes.windll.user32


class WindowTransparency:
    """
    高效窗口透明度控制器
    解决了快速操作下的线程竞态和透明度残留问题
    """

    def __init__(self, target_alpha: int = 200, restore_alpha: int = 255, interval: float = 0.002):
        self.target_alpha = max(0, min(255, target_alpha))
        self.restore_alpha = max(0, min(255, restore_alpha))
        self.interval = max(0.001, interval)

        # 核心：按窗口句柄管理停止事件，防止全局干扰
        # { hwnd: threading.Event }
        self._tasks: Dict[int, threading.Event] = {}
        self._lock = threading.Lock()

    def _ensure_layered(self, hwnd: int) -> bool:
        """确保窗口拥有分层属性"""
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not (ex_style & WS_EX_LAYERED):
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
            # 初始设为完全不透明，防止从 0 闪烁
            user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
            return True
        return False

    def _get_current_alpha(self, hwnd: int) -> int:
        """安全获取当前透明度"""
        alpha = ctypes.c_ubyte(255)
        if user32.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(alpha), None):
            return alpha.value
        return 255

    def _animate_task(self, hwnd: int, start: int, target: int, stop_event: threading.Event):
        """执行具体的动画逻辑"""
        try:
            diff = target - start
            if diff == 0:
                return

            step = 1 if diff > 0 else -1
            # 动态步长：距离越远走得越快，增加灵敏度
            actual_step = step * (2 if abs(diff) > 50 else 1)

            current = start
            while not stop_event.is_set():
                current += actual_step

                # 边界检查
                if (step > 0 and current >= target) or (step < 0 and current <= target):
                    user32.SetLayeredWindowAttributes(
                        hwnd, 0, target, LWA_ALPHA)
                    break

                user32.SetLayeredWindowAttributes(hwnd, 0, current, LWA_ALPHA)
                time.sleep(self.interval)
        finally:
            # 任务结束，尝试清理字典（仅当没有新任务覆盖时）
            with self._lock:
                if self._tasks.get(hwnd) == stop_event:
                    self._tasks.pop(hwnd, None)

    def set_transparent(self, hwnd: int, alpha: int = None):
        """带动画地设置透明度"""
        if not hwnd or hwnd == 0:
            return

        target = alpha if alpha is not None else self.target_alpha
        target = max(0, min(255, target))

        # 1. 预处理
        self._ensure_layered(hwnd)
        current_alpha = self._get_current_alpha(hwnd)

        # 2. 线程安全地替换任务
        with self._lock:
            # 如果该窗口已有动画正在运行，令其停止
            if hwnd in self._tasks:
                self._tasks[hwnd].set()

            # 创建新的停止信号
            new_stop_event = threading.Event()
            self._tasks[hwnd] = new_stop_event

            # 启动新动画线程
            t = threading.Thread(
                target=self._animate_task,
                args=(hwnd, current_alpha, target, new_stop_event),
                daemon=True
            )
            t.start()

    def restore(self, hwnd: int, use_animation: bool = True):
        """
        恢复窗口不透明
        use_animation: 是否使用动画。如果点击极快依然有问题，建议设为 False
        """
        if not use_animation:
            # 暴力恢复：停止所有动画并直接设为不透明
            with self._lock:
                if hwnd in self._tasks:
                    self._tasks[hwnd].set()
            user32.SetLayeredWindowAttributes(
                hwnd, 0, self.restore_alpha, LWA_ALPHA)
        else:
            self.set_transparent(hwnd, self.restore_alpha)


def if_transparent(hwnd: int) -> bool:
    """判断窗口是否处于透明状态（留有余量）"""
    alpha = ctypes.c_ubyte(255)
    if not user32.GetLayeredWindowAttributes(hwnd, None, ctypes.byref(alpha), None):
        return False
    return alpha.value < 253


# --- 使用示例 ---
if __name__ == "__main__":
    # 模拟监听逻辑
    ctrl = WindowTransparency(target_alpha=220, interval=0.003)

    # 模拟快速切换
    test_hwnd = user32.GetForegroundWindow()
    print(f"正在对窗口 {test_hwnd} 进行压力测试...")

    for _ in range(5):
        ctrl.set_transparent(test_hwnd)
        time.sleep(0.05)  # 极短点击
        ctrl.restore(test_hwnd)
        time.sleep(0.05)
