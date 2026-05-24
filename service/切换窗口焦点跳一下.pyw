import ctypes
from ctypes import wintypes
import os
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

# 常量定义
GWL_STYLE = -16
GW_OWNER = 3
WS_CHILD = 0x40000000
WS_CAPTION = 0x00C00000  # (WS_BORDER | WS_DLGFRAME)

# ====================================================================
# 【高精追踪器】
# last_valid_hwnd: 记录上一个真正跳过的大窗口
# last_component_hwnd: 记录上一个触发了回调但被拦截的组件窗口(如右键菜单)
# ====================================================================
last_valid_hwnd = 0
last_component_hwnd = 0


def main():
    ole32.CoInitialize(None)

    # ==================== 工业级物理动画全参数控制面板 ====================
    AMPLITUDE = 20  # 最大跳动高度 (px)
    STEP_SIZE = 4  # 每次位移步长 (px)
    STEP_DELAY = 0.01  # 像素位移阻尼 (s)
    BOUNCE_OVERSHOOT = 0  # 回弹下探深度 (px)
    BOUNCE_COUNT = 0  # 回弹余震次数
    TASKBAR_DELAY = 0.12  # 任务栏补偿延迟 (s)
    MINIMIZE_TIMEOUT = 0.4  # 最小化侦测超时 (s)
    CHECK_INTERVAL = 0.01  # 状态扫描步长 (s)
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
        global last_valid_hwnd, last_component_hwnd

        if not hwnd:
            return

        # ====================================================================
        # 1. 全维样式决策
        # ====================================================================
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)

        # 铁律拦截：凡是带 WS_CHILD 的真子控件（按钮/输入框），直接拦截
        if style & WS_CHILD:
            return

        # 行为拦截：如果没有标准标题栏，说明它是个组件窗口（右键菜单、下拉气泡等）
        if not (style & WS_CAPTION):
            owner_hwnd = user32.GetWindow(hwnd, GW_OWNER)
            if owner_hwnd and owner_hwnd != hwnd:
                # 【关键盯防】记录下这个正在作怪的组件句柄，供下一步回弹校验使用
                last_component_hwnd = hwnd
                return

        # ====================================================================
        # 2. 血缘级防回弹熔断器（解决 Win+Tab 罢工 Bug）
        # ====================================================================
        # 如果上一步有组件登记在案，我们需要看看当前大窗口是不是它的“亲长辈”
        if last_component_hwnd:
            # 找到这个组件对应的顶级宿主窗口 (GA_ROOT = 2)
            component_root = user32.GetAncestor(last_component_hwnd, 2)

            # 如果组件的宿主，恰好就是当前拿焦点的窗口，说明这才是真正的“菜单关闭焦点回弹”
            if component_root == hwnd:
                # 成功拦截纯粹的回弹，且清空组件追踪，防止后续二次误伤
                last_component_hwnd = 0
                return

            # 如果走到这，说明当前的 hwnd 和刚才的组件没有任何血缘关系（比如是通过 Win+Tab 切过来的）
            # 我们主动清除过期组件标记，允许它放行跳动！
            last_component_hwnd = 0

        # 如果和组件无关，但和上次跳过的窗口一模一样（极其罕见的系统误触发重复焦点），也予以拦截
        if hwnd == last_valid_hwnd and not last_component_hwnd:
            return
        # ====================================================================

        # 3. 判定鼠标左键(0x01)、右键(0x02) 或 中键(0x04) 是否按下
        is_lbutton_down = (user32.GetAsyncKeyState(0x01) & 0x8000) != 0
        is_rbutton_down = (user32.GetAsyncKeyState(0x02) & 0x8000) != 0
        is_mbutton_down = (user32.GetAsyncKeyState(0x04) & 0x8000) != 0

        if is_lbutton_down or is_rbutton_down or is_mbutton_down:
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))

            hwnd_under_mouse = user32.WindowFromPoint(pt)

            if hwnd_under_mouse:
                top_mouse_hwnd = user32.GetAncestor(hwnd_under_mouse, 2)
                if not top_mouse_hwnd:
                    top_mouse_hwnd = hwnd_under_mouse

                top_active_hwnd = user32.GetAncestor(hwnd, 2)
                if not top_active_hwnd:
                    top_active_hwnd = hwnd

                if top_mouse_hwnd == top_active_hwnd:
                    return

        # ====================================================================
        # 4. 确认放行：更新大窗口暂存器，触发物理动画
        # ====================================================================
        last_valid_hwnd = hwnd

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

    print("windows_next 焦点引擎 [血缘追踪防回弹版] 已成功合围启动。")

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
