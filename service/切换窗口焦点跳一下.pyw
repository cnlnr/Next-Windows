import ctypes
from ctypes import wintypes
import os
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

# 常量定义
GWL_STYLE = -16
WS_CHILD = 0x40000000
GA_ROOTOWNER = 3  # 追溯到最顶层的独立拥有者窗口（能代表任务栏/标题视窗的那个老祖宗）

# ====================================================================
# 【极简顶级视窗追踪器】
# last_root_hwnd: 记录上一个真正触发了跳动动作的“顶级独立大窗口”句柄
# ====================================================================
last_root_hwnd = 0


def main():
    ole32.CoInitialize(None)

    # ==================== 工业级物理动画全参数控制面板 ====================
    AMPLITUDE = 20
    STEP_SIZE = 4
    STEP_DELAY = 0.01
    BOUNCE_OVERSHOOT = 0
    BOUNCE_COUNT = 0
    TASKBAR_DELAY = 0.12
    MINIMIZE_TIMEOUT = 0.4
    CHECK_INTERVAL = 0.01
    # ====================================================================

    def outer_callback(
        hWinEventHook,
        event,
        hwnd,
        idObject,
        idChild,
        dwEventThread,
        dwmsEventTime,
    ):
        global last_root_hwnd

        if not hwnd:
            return

        # ====================================================================
        # 1. 铁律拦截
        # ====================================================================
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        if style & WS_CHILD:
            return

        # ====================================================================
        # 2. 顶级大牌面抽取 (降维打击 Edge 插件干扰)
        # ====================================================================
        # 无论当前拿到焦点的是 Edge 网页、Edge 菜单、还是 Edge 顽固的插件控件，
        # 通过 GA_ROOTOWNER 拔出来的，永远只能是 Edge 的那个顶层主窗体句柄。
        current_root = user32.GetAncestor(hwnd, GA_ROOTOWNER)
        if not current_root:
            current_root = hwnd

        # 如果提取出来的顶级大窗口跟上一次跳过的一模一样，说明根本没换软件，直接拦截
        if current_root == last_root_hwnd:
            return
        # ====================================================================

        # 3. 鼠标按压判定（防止拖拽大窗口或点击内部控件引起的误跳）
        is_lbutton_down = (user32.GetAsyncKeyState(0x01) & 0x8000) != 0
        is_rbutton_down = (user32.GetAsyncKeyState(0x02) & 0x8000) != 0
        is_mbutton_down = (user32.GetAsyncKeyState(0x04) & 0x8000) != 0

        if is_lbutton_down or is_rbutton_down or is_mbutton_down:
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            hwnd_under_mouse = user32.WindowFromPoint(pt)
            if hwnd_under_mouse:
                mouse_root = user32.GetAncestor(hwnd_under_mouse, GA_ROOTOWNER)
                if not mouse_root:
                    mouse_root = hwnd_under_mouse

                # 如果鼠标按下的窗口顶级归属和当前激活的顶级归属一致，说明是内部点击操作，拦截
                if mouse_root == current_root:
                    # 哪怕由于点击内部被拦截，它也已经是当前合法的顶级拥有者了，更新状态保持同步
                    last_root_hwnd = current_root
                    return

        # ====================================================================
        # 4. 确认放行：洗牌顶级句柄状态，触发物理跳动
        # ====================================================================
        # 记录这次跳跃的独立顶级大窗口
        last_root_hwnd = current_root

        # 始终让当前事件真正触发的当前窗口（hwnd）去执行跳动动画
        window_jump.event_callback_handler(
            hwnd,
            amplitude=AMPLITUDE,
            step_size=STEP_SIZE,
            step_delay=STEP_DELAY,
            bounce_overshoot=BOUNCE_OVERSHOOT,
            bounce_count=BOUNCE_COUNT,
            taskbar_delay=TASKBAR_DELAY,
            minimize_timeout=MINIMIZE_TIMEOUT,
            check_interval=CHECK_INTERVAL,
        )

    global proc_instance
    proc_instance = window_jump.WinEventProcType(outer_callback)

    hook = user32.SetWinEventHook(
        window_jump.EVENT_SYSTEM_FOREGROUND,
        window_jump.EVENT_SYSTEM_FOREGROUND,
        0,
        proc_instance,
        0,
        0,
        window_jump.WINEVENT_OUTOFCONTEXT,
    )

    if not hook:
        print("错误：无法注册 WinEvent 钩子。")
        return

    print("windows_next 焦点引擎 [顶级等价验证版] 已合围启动。")

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
