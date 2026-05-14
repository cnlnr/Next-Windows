from next_windows.任务栏滚动切换应用 import TaskbarScroll
from pynput.keyboard import Key, Controller

kb = Controller()


class MySwitch(TaskbarScroll):
    def on_scroll(self, reverse):
        # ========== 这里你随便写任何快捷键 ==========
        # 示例 1：Alt+Tab
        kb.press(Key.alt)
        if reverse:
            with kb.pressed(Key.shift):
                kb.tap(Key.tab)
        else:
            kb.tap(Key.tab)

        # 示例 2：Ctrl+Win+Alt+Tab or Esc
        # with kb.pressed(Key.ctrl, Key.cmd, Key.alt):
        #     if reverse:
        #         with kb.pressed(Key.shift):
        #             kb.tap(Key.tab)
        #     else:
        #         kb.tap(Key.tab)


with MySwitch(sensitivity=1):
    input("按回车退出...")
