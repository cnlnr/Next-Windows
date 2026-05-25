import ctypes
from ctypes import wintypes
import os
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
ole32 = ctypes.windll.ole32

# ==================== 性能优化：预分配全局缓冲区 ====================
# 避免在 WinEvent 高频回调内部进行内存分配与销毁
CLASS_BUF = ctypes.create_unicode_buffer(256)
EXE_PATH_BUF = ctypes.create_unicode_buffer(1024)

# 常量定义
GWL_STYLE = -16
WS_CHILD = 0x40000000
GA_ROOTOWNER = 3  # 追溯到最顶层的独立拥有者窗口
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

# ====================================================================
# 【顶级视窗追踪器】
# last_root_hwnd: 始终记录上一个真正触发了跳动动作的“顶级独立大窗口”句柄
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

    # 预先计算标准系统 explorer.exe 的绝对路径（转为小写方便后续比对）
    system_root = os.environ.get("SystemRoot", "C:\\Windows")
    explorer_target_path = os.path.join(system_root, "explorer.exe").lower()

    # 预先计算通知中心与打开方式的绝对路径
    shell_experience_target_path = os.path.join(
        system_root, "systemapps", "shellexperiencehost_cw5n1h2txyewy", "shellexperiencehost.exe"
    ).lower()
    openwith_target_path = os.path.join(
        system_root, "System32", "openwith.exe").lower()

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
        # 新增 1. XamlExplorerHostIslandWindow 类名与路径安全熔断拦截
        # ====================================================================
        # 极速类名筛选（复用全局缓冲区）
        user32.GetClassNameW(hwnd, CLASS_BUF, 256)

        # 【新增拦截 A】虚拟桌面切换器类名，直接在这里秒杀拦截
        if CLASS_BUF.value == "VirtualDesktopHotkeySwitcher":
            return

        # 命中目标类名后，才触发路径校验（完美短路，不影响普通窗口切换性能）
        # 【老代码扩充】加入 Windows.UI.Core.CoreWindow 拦截判断，共用路径查询通道
        if CLASS_BUF.value == "XamlExplorerHostIslandWindow" or CLASS_BUF.value == "Windows.UI.Core.CoreWindow":
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            if pid.value:
                h_process = kernel32.OpenProcess(
                    PROCESS_QUERY_LIMITED_INFORMATION, False, pid
                )
                if h_process:
                    size = wintypes.DWORD(len(EXE_PATH_BUF))
                    # 高效获取进程完整路径
                    success = kernel32.QueryFullProcessImageNameW(
                        h_process, 0, EXE_PATH_BUF, ctypes.byref(size)
                    )
                    kernel32.CloseHandle(h_process)

                    if success:
                        current_exe_path = EXE_PATH_BUF.value.lower()

                        # 确认为系统合法的 explorer.exe 触发，执行熔断拦截
                        if CLASS_BUF.value == "XamlExplorerHostIslandWindow" and current_exe_path == explorer_target_path:
                            return

                        # 【新增拦截 B】确认为通知中心进程发出的 CoreWindow，执行熔断拦截
                        if CLASS_BUF.value == "Windows.UI.Core.CoreWindow" and current_exe_path == shell_experience_target_path:
                            return

        # 【新增拦截 C】由于 OpenWith 顶级类名不固定，在其进入子窗口拦截前，直接通过 PID 穿透检测其路径
        pid_ow = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_ow))
        if pid_ow.value:
            h_proc_ow = kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid_ow)
            if h_proc_ow:
                size_ow = wintypes.DWORD(len(EXE_PATH_BUF))
                success_ow = kernel32.QueryFullProcessImageNameW(
                    h_proc_ow, 0, EXE_PATH_BUF, ctypes.byref(size_ow))
                kernel32.CloseHandle(h_proc_ow)
                if success_ow and EXE_PATH_BUF.value.lower() == openwith_target_path:
                    return

        # ====================================================================
        # 2. 铁律拦截 (子窗口直接过滤)
        # ====================================================================
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        if style & WS_CHILD:
            return

        # ====================================================================
        # 3. 顶级大牌面抽取
        # ====================================================================
        # 剥离所有嵌套、独立悬浮插件控件的干扰，强行获取它所属的独立顶级大窗口
        current_root = user32.GetAncestor(hwnd, GA_ROOTOWNER)
        if not current_root:
            current_root = hwnd

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
        # 若想切回此模式，请注释掉下方的【模式 B】，并将下方代码取消注释
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
        # 【模式 B】谁当前拿焦点谁跳（可能是组件窗口跳,试试edge的Dark Reader插件）
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

    print(
        "windows_next 焦点引擎 [顶级独立父窗+XamlIsland安全校验版] 已启动。"
    )

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
