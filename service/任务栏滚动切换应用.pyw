import time
from pynput import mouse
from next_windows.任务栏滚动切换应用 import WinEngine


class NextSwitcher:
    def __init__(self, mode="persistent", sensitivity=1):
        """
        :param mode: "persistent" 或 "standard"
        :param sensitivity: 整数，滚轮滚动的物理格数触发阈值
        """
        self.engine = WinEngine()
        self.mode = mode
        self.sensitivity = int(sensitivity)  # 纯整数逻辑
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
            if current_time - self.last_time < 0.05:
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


if __name__ == "__main__":
    # 模式选择:
    # "persistent" (对应 Ctrl+Win+Alt+Tab) 扩展屏下可能有bug
    # "standard"   (对应 Alt+Tab)
    # sensitivity: 整数格数触发阈值 (1 代表滚一格换一个)
    app = NextSwitcher(mode="standard", sensitivity=1)
    app.run()
