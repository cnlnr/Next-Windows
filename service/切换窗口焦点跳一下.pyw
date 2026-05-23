import ctypes
from ctypes import wintypes
import os
import next_windows.切换窗口焦点跳一下 as window_jump

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
ole32 = ctypes.windll.ole32

# 预先分配好固定大小的缓冲区，避免回调内部高频分配、销毁内存
CLASS_BUF = ctypes.create_unicode_buffer(256)
EXE_PATH_BUF = ctypes.create_unicode_buffer(1024)

# 常量定义
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


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

    # 预先计算标准系统 explorer.exe 的绝对路径（转为小写方便后续比对）
    system_root = os.environ.get("SystemRoot", "C:\\Windows")
    explorer_target_path = os.path.join(system_root, "explorer.exe").lower()

    def outer_callback(
        hWinEventHook,
        event,
        hwnd,
        idObject,
        idChild,
        dwEventThread,
        dwmsEventTime,
    ):
        if not hwnd:
            return

        # 1. 极速类名筛选（复用全局缓冲区）
        user32.GetClassNameW(hwnd, CLASS_BUF, 256)

        # 2. 命中目标类名后，才触发路径校验（完美短路，不影响普通窗口切换性能）
        if CLASS_BUF.value == "XamlExplorerHostIslandWindow":
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

                    # 确认为系统合法的 explorer.exe 触发，执行熔断拦截
                    if success and EXE_PATH_BUF.value.lower() == explorer_target_path:
                        return

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

        # 4. 放行其余正常切换事件
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

    print("windows_next 焦点引擎 [类名+路径安全校验版] 已启动。")

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
