"""将鼠标移动到左上角出发相应操作"""
import time
from pynput.keyboard import Key
from next_windows.左上角 import create_hotzone_checker, create_key_trigger, mouse
import time

# 1. 定义检测器
checker = create_hotzone_checker(threshold=10)


# 例子 A: 模拟 Win + Tab (打开关闭任务视图)
action = create_key_trigger(Key.cmd, Key.tab)

# 例子 B: 模拟 Win + 1 (打开或关闭第一个窗口)
# action = create_key_trigger(Key.cmd, Key.one)

# 例子 C: 模拟 Alt + Esc (切换应用) 推荐
# action = create_key_trigger(Key.alt, Key.esc)

m_controller = mouse.Controller()

try:
    while True:
        if checker(m_controller.position):
            action()  # 执行你定义的动作
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
