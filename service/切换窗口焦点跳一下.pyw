import ctypes
from ctypes import wintypes
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32


def main():
    ole32.CoInitialize(None)

    # ==================== 工业级物理动画全参数控制面板 ====================
    AMPLITUDE = 20        # 最大跳动高度 (px)
    STEP_SIZE = 4          # 每次位移步长 (px) —— 值越大跳得越快越硬朗
    STEP_DELAY = 0.01       # 像素位移阻尼 (s)
    BOUNCE_OVERSHOOT = 0         # 回弹下探深度 (px)
    BOUNCE_COUNT = 0         # 回弹余震次数
    TASKBAR_DELAY = 0.12      # 任务栏补偿延迟 (s)
    MINIMIZE_TIMEOUT = 0.4       # 最小化侦测超时 (s)
    CHECK_INTERVAL = 0.01      # 状态扫描步长 (s)
    # ====================================================================

    # 在启动时精准定位 Win+Tab 任务视图的系统组件句柄（兼容中英文系统环境）
    task_view_hwnd = user32.FindWindowW("Windows.UI.Core.CoreWindow", "任务视图")
    if not task_view_hwnd:
        task_view_hwnd = user32.FindWindowW(
            "Windows.UI.Core.CoreWindow", "Task View")

    def outer_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if not hwnd:
            return

        # 1. 纯净句柄黑名单熔断：如果是 Win+Tab 唤出的任务视图句柄，直接拦截
        if hwnd == task_view_hwnd:
            return

        # 2. 判定鼠标左键(0x01)、右键(0x02) 或 中键(0x04) 是否按下
        is_lbutton_down = (user32.GetAsyncKeyState(0x01) & 0x8000) != 0
        is_rbutton_down = (user32.GetAsyncKeyState(0x02) & 0x8000) != 0
        is_mbutton_down = (user32.GetAsyncKeyState(0x04) & 0x8000) != 0

        # 只要三键之一被按下，就进入窗口重合度探测逻辑
        if is_lbutton_down or is_rbutton_down or is_mbutton_down:
            # 获取当前鼠标光标的绝对坐标
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))

            # 探测鼠标正下方的窗口句柄
            hwnd_under_mouse = user32.WindowFromPoint(pt)

            if hwnd_under_mouse:
                # 穿透获取鼠标下窗口的顶级祖先
                top_mouse_hwnd = user32.GetAncestor(
                    hwnd_under_mouse, 2)  # GA_ROOT = 2
                if not top_mouse_hwnd:
                    top_mouse_hwnd = hwnd_under_mouse

                # 获取当前新激活窗口的顶级祖先
                top_active_hwnd = user32.GetAncestor(hwnd, 2)
                if not top_active_hwnd:
                    top_active_hwnd = hwnd

                # 如果按了任意鼠标键，且鼠标下的窗口和新激活的窗口是同一个，判定为正常鼠标点击窗口内部，直接拦截
                if top_mouse_hwnd == top_active_hwnd:
                    return

        # 此时已经完美分流：
        # - 鼠标点击应用窗体内部 -> 被拦截 (return)
        # - Win+Tab 呼出界面 -> 被黑名单句柄熔断 (return)
        # - 键盘快捷键（Alt+Tab）、点击底部任务栏切换窗口、Win+D 返回桌面 -> 完美放行，正常跳动
        window_jump.event_callback_handler(
            hwnd,
            amplitude=AMPLITUDE,
            step_size=STEP_SIZE,
            step_delay=STEP_DELAY,
            bounce_overshoot=BOUNCE_OVERSHOOT,
            bounce_count=BOUNCE_COUNT,
            taskbar_delay=TASKBAR_DELAY,
            minimize_timeout=MINIMIZE_TIMEOUT,
            check_interval=CHECK_INTERVAL
        )

    global proc_instance
    proc_instance = window_jump.WinEventProcType(outer_callback)

    hook = user32.SetWinEventHook(
        window_jump.EVENT_SYSTEM_FOREGROUND, window_jump.EVENT_SYSTEM_FOREGROUND,
        0, proc_instance, 0, 0, window_jump.WINEVENT_OUTOFCONTEXT
    )

    if not hook:
        print("错误：无法注册 WinEvent 钩子。")
        return

    print("windows_next 焦点引擎 [句柄级纯净拦截版] 已启动。")

    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWinEvent(hook)
        ole32.CoUninitialize()


if __name__ == "__main__":
    main()
