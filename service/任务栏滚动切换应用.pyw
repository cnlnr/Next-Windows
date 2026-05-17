# 文件名: main.py
import time
from pynput.keyboard import Key
# 从我们刚刚写好的库文件中导入基类
from next_windows.任务栏滚动切换应用 import TaskbarScroll


class MySwitch(TaskbarScroll):
    def on_scroll(self, reverse):
        # 1. 滚动开始时，先确保 Alt 键被按住了
        self.press_alt()

        # 2. 根据滚动方向决定是 Tab 还是 Shift+Tab
        if reverse:
            with self.kb.pressed(Key.shift):
                self.kb.tap(Key.tab)
        else:
            self.kb.tap(Key.tab)


if __name__ == "__main__":
    # 这里的 sensitivity 可以根据你的习惯调整，数值越大滚动越迟钝
    with MySwitch(sensitivity=1) as swiper:
        print("=" * 50)
        print("【任务栏滚轮切换应用】已启动！")
        print(" -> 行为：在任务栏滚动滚轮触发 Alt+Tab")
        print(" -> 释放：鼠标移出任务栏或按下 Ctrl+C 退出时，将自动释放 Alt 键")
        print("=" * 50)

        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n检测到退出信号，正在安全清理按键状态...")
