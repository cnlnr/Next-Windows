# 文件名: main.py
import time
from pynput.keyboard import Key
# 从库文件中导入基类
from next_windows.任务栏滚动切换应用 import TaskbarScroll


class MySwitch(TaskbarScroll):
    def on_scroll(self, reverse):
        # 1. 确保 Alt 键被按住
        self.press_alt()

        # 2. 没有任何延迟，直接发送 Tab 信号
        if reverse:
            with self.kb.pressed(Key.shift):
                self.kb.tap(Key.tab)
        else:
            kb_tap = self.kb.tap(Key.tab)


if __name__ == "__main__":
    # 实例化不再需要传入 sensitivity 参数
    with MySwitch() as swiper:
        print("=" * 50)
        print("【极速模式】任务栏滚轮切换已启动！")
        print(" -> 行为：滚轮每动一格，立刻切换一下应用（零延迟）")
        print(" -> 释放：鼠标移出任务栏自动释放 Alt 键")
        print("=" * 50)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n程序已安全退出。")
