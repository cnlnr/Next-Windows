import time
from pynput import mouse, keyboard


def create_hotzone_checker(threshold=10):
    """
    状态检测闭包：检测鼠标是否“新进入”热区
    """
    context = {'already_inside': False}

    def check(pos):
        x, y = pos
        is_now_inside = x <= threshold and y <= threshold

        triggered = False
        if is_now_inside and not context['already_inside']:
            triggered = True

        context['already_inside'] = is_now_inside
        return triggered
    return check


def create_key_trigger(*keys):
    """
    按键触发闭包：支持单个键或组合键
    用法: 
        trigger = create_key_trigger(Key.cmd)
        trigger = create_key_trigger(Key.ctrl, 'c')
    """
    k_controller = keyboard.Controller()

    def trigger():
        # 按下所有键
        for key in keys:
            k_controller.press(key)
        # 逆序释放所有键
        for key in reversed(keys):
            k_controller.release(key)

    return trigger
