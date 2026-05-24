import ctypes
from ctypes import wintypes
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

# 常量定义
GWL_STYLE = -16
GW_OWNER = 3
WS_CHILD = 0x40000000
WS_CAPTION = 0x00C00000  # (WS_BORDER | WS_DLGFRAME)
GA_ROOTOWNER = 3  # 追溯到最顶层的独立拥有者窗口（任务栏/大视窗视角的根源句柄）

# ====================================================================
# 【高精顶级视窗追踪器】
# last_root_hwnd: 始终记录上一个真正触发了跳动动作的“顶级独立大窗口”句柄
# last_component_hwnd: 记录上一个触发了回调但被拦截的组件窗口(如右键菜单、下拉气泡)
# ====================================================================
last_root_hwnd = 0
last_component_hwnd = 0


def main():
    ole32.CoInitialize(None)

    # ==================== 工业级物理动画全参数控制面板 ====================
    AMPLITUDE = 20
    STEP_SIZE = 4
    STEP_DELAY = 0.009
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
        global last_root_hwnd, last_component_hwnd

        if not hwnd:
            return

        # ====================================================================
        # 1. 铁律拦截与组件窗拦截（老代码核心第一步）
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
        # 2. 顶级大牌面抽取
        # ====================================================================
        # 剥离所有嵌套、独立悬浮插件控件的干扰，强行获取它所属的独立顶级大窗口
        current_root = user32.GetAncestor(hwnd, GA_ROOTOWNER)
        if not current_root:
            current_root = hwnd

        # ====================================================================
        # 3. 血缘级防回弹熔断器（无缝保留你的 Win+Tab 解决方案）
        # ====================================================================
        if last_component_hwnd:
            # 找到这个组件对应的顶级宿主大窗口
            component_root = user32.GetAncestor(
                last_component_hwnd, GA_ROOTOWNER)
            if not component_root:
                component_root = last_component_hwnd

            # 如果组件的宿主，恰好就是当前拿焦点的顶级窗口，说明这才是真正的“菜单关闭焦点回弹”
            if component_root == current_root:
                # 成功拦截纯粹的回弹，且清空组件追踪，防止后续二次误伤
                last_component_hwnd = 0
                return

            # 如果走到这，说明当前的 current_root 和刚才的组件没有任何血缘关系（比如是通过 Win+Tab 切过来的）
            # 主动清除过期组件标记，允许它放行跳动！
            last_component_hwnd = 0

        # 如果提取出来的顶级老祖宗跟上一次跳过的一模一样，说明是在同软件内折腾，直接拦截
        if current_root == last_root_hwnd:
            return
        # ====================================================================

        # 4. 鼠标按压判定（防止拖拽大窗口或点击内部控件引起的误跳）
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

                # 如果鼠标按下的窗口顶级归属和当前激活的顶级归属一致，说明是内部操作，拦截
                if mouse_root == current_root:
                    last_root_hwnd = current_root
                    return

        # ====================================================================
        # 5. 确认放行：洗牌顶级状态，触发跳动动画
        # ====================================================================
        # 记录这次跳跃的独立顶级大窗口
        last_root_hwnd = current_root

        # --------------------------------------------------------------------
        # 【模式 A】强制让顶级父窗口整体完成灵动一跳（免疫插件小方块乱抖）
        # --------------------------------------------------------------------
        # window_jump.event_callback_handler(
        #     current_root,
        #     amplitude=AMPLITUDE,
        #     step_size=STEP_SIZE,
        #     step_delay=STEP_DELAY,
        #     bounce_overshoot=BOUNCE_OVERSHOOT,
        #     bounce_count=BOUNCE_COUNT,
        #     taskbar_delay=TASKBAR_DELAY,
        #     minimize_timeout=MINIMIZE_TIMEOUT,
        #     check_interval=CHECK_INTERVAL,
        # )

        # --------------------------------------------------------------------
        # 【模式 B】谁当前拿焦点谁跳
        # --------------------------------------------------------------------
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
        # --------------------------------------------------------------------

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

    print("windows_next 焦点引擎 [顶级独立父窗+血缘防回弹版] 已成功融合启动。")

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
