import ctypes
from ctypes import wintypes

# WinEvent constants
user32 = ctypes.windll.user32
EVENT_SYSTEM_MOVESIZESTART = 0x000A
EVENT_SYSTEM_MOVESIZEEND = 0x000B
WINEVENT_OUTOFCONTEXT = 0x0000

# WinEvent 回调类型
WinEventProcType = ctypes.WINFUNCTYPE(
    None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
    wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD
)


def wait_for_move_event():
    """阻塞直到检测到 MOVE/RESIZE 开始或结束事件。

    返回 (is_start, hwnd)
    - is_start == True  ：检测到 EVENT_SYSTEM_MOVESIZESTART（开始拖动）
    - is_start == False ：检测到 EVENT_SYSTEM_MOVESIZEEND（结束/松开）
    """
    result = {"evt": None, "hwnd": None}

    def _cb(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if event == EVENT_SYSTEM_MOVESIZESTART:
            result["evt"] = True
            result["hwnd"] = hwnd
            user32.PostQuitMessage(0)
        elif event == EVENT_SYSTEM_MOVESIZEEND:
            result["evt"] = False
            result["hwnd"] = hwnd
            user32.PostQuitMessage(0)

    proc = WinEventProcType(_cb)

    hook = user32.SetWinEventHook(
        EVENT_SYSTEM_MOVESIZESTART,
        EVENT_SYSTEM_MOVESIZEEND,
        0,
        proc,
        0, 0,
        WINEVENT_OUTOFCONTEXT
    )

    if not hook:
        raise RuntimeError("SetWinEventHook failed")

    # 阻塞消息循环，直到回调中调用 PostQuitMessage
    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    finally:
        user32.UnhookWinEvent(hook)

    return result["evt"], result["hwnd"]


if __name__ == "__main__":
    while True:
        print("Waiting for move/resize event...")
        is_start, hwnd = wait_for_move_event()
        if is_start:
            print(f"Detected MOVE START: HWND={hwnd}")
        else:
            print(f"Detected MOVE END:   HWND={hwnd}")
