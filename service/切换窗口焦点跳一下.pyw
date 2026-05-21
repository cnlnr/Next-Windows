import ctypes
from ctypes import wintypes
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32


def main():
    ole32.CoInitialize(None)

    # ==================== 用户自定义参数配置面板 ====================
    AMPLITUDE = 18     # 跳动幅度：单位像素 (px)
    DURATION = 0.08   # 动画时间：单位秒 (s)
    TASKBAR_DELAY = 0.13   # 任务栏延迟：最小化恢复时的盲憋等待时间 (s)
    # =============================================================

    # 利用闭包（Closure）机制，在纯函数架构下完美传递用户自定义参数
    def outer_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        window_jump.event_callback_handler(
            hwnd,
            amplitude=AMPLITUDE,
            duration=DURATION,
            taskbar_delay=TASKBAR_DELAY
        )

    # 必须在函数内部保持住这个局部变量的全局引用，防止被 GC 回收
    global proc_instance
    proc_instance = window_jump.WinEventProcType(outer_callback)

    hook = user32.SetWinEventHook(
        window_jump.EVENT_SYSTEM_FOREGROUND, window_jump.EVENT_SYSTEM_FOREGROUND,
        0, proc_instance, 0, 0, window_jump.WINEVENT_OUTOFCONTEXT
    )

    if not hook:
        print("错误：无法注册 WinEvent 钩子。")
        return

    print("windows_next 焦点引擎 [用户调参版] 已启动。")
    print(
        f"当前配置 -> 弹跳: {AMPLITUDE}px | 耗时: {DURATION}s | 任务栏补偿: {TASKBAR_DELAY}s")

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
