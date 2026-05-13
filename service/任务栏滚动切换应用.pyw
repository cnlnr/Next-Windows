import time
from pynput import mouse
from next_windows.任务栏滚动切换应用 import WinEngine


class NextSwitcher:
    def __init__(self, mode="persistent"):
        self.engine = WinEngine()
        self.last_scroll_time = 0
        self.cooldown = 0.02  # 稍微增加冷却，防止持久化界面滚动过快
        self.mode = mode  # "standard" 或 "persistent"

    def on_scroll(self, x, y, dx, dy):
        if not self.engine.is_mouse_on_taskbar(x, y):
            if self.mode == "standard":
                self.engine.stop_switching()
            return

        current_time = time.time()
        if current_time - self.last_scroll_time < self.cooldown:
            return

        if abs(dy) >= 0.1:
            is_reverse = dy > 0  # 向上滚是反向

            if self.mode == "persistent":
                # 使用 Ctrl + Win + Alt + Tab
                self.engine.switch_persistent(reverse=is_reverse)
            else:
                # 使用 Alt + Tab
                self.engine.switch_standard(reverse=is_reverse)

            self.last_scroll_time = current_time

    def on_move(self, x, y):
        # 只有模式 1 需要处理离开即确认的逻辑
        if self.mode == "standard":
            if not self.engine.is_mouse_on_taskbar(x, y):
                self.engine.stop_switching()

    def run(self):
        print(f"Next-Windows Switcher 启动 | 当前模式: {self.mode}")
        with mouse.Listener(on_scroll=self.on_scroll, on_move=self.on_move) as listener:
            listener.join()


if __name__ == "__main__":
    # 在这里选择模式：standard (Alt+Tab) 或 persistent (Ctrl+Win+Alt+Tab)
    app = NextSwitcher(mode="standard")
    app.run()
