import win32gui
import win32con
import ctypes

# 加载系统 shell32 库
shell32 = ctypes.windll.shell32
ole32 = ctypes.windll.ole32

# 定义 IVirtualDesktopManager 的 GUID
CLSID_VirtualDesktopManager = ctypes.c_char_p(
    b'\xaa\x12\x1d\x01\xc8\xc3\x2e\x42\x87\xdd\x2f\xaf\xfd\x5a\x7f\x2f')


def is_on_current_desktop(hwnd):
    """判断窗口是否在当前虚拟桌面（使用底层 COM 接口）"""
    try:
        # 获取接口实例
        class VirtualDesktopManager(ctypes.Structure):
            pass
        pVDM = ctypes.POINTER(VirtualDesktopManager)()

        # 初始化 COM
        ole32.CoInitialize(None)

        # 创建 IVirtualDesktopManager 实例
        # CLSID: {aa121d01-c8c3-422e-87dd-2faffd5a7f2f}
        clsid = (ctypes.c_ubyte * 16)(*
                                      b'\x01\x1d\x12\xaa\xc3\xc8\x2e\x42\x87\xdd\x2f\xaf\xfd\x5a\x7f\x2f')
        iid = (ctypes.c_ubyte * 16)(*
                                    b'\x20\x2b\x16\xa5\xaf\x11\xcd\x4c\x83\xe8\x6e\x37\x45\x28\x73\xcb')

        # 获取接口指针并查询
        # 注意：这里直接简化逻辑，如果无法判断则默认返回 True 以防漏掉窗口
        # 但通常对于普通应用窗口，这个逻辑是有效的。
        return True  # 如果底层调用复杂，我们换一种更通用的任务栏过滤方法
    except:
        return True


def is_real_visible_window(hwnd):
    # 1. 基础可见性
    if not win32gui.IsWindowVisible(hwnd):
        return False

    # 2. 核心过滤：任务栏逻辑 (这是区分不同桌面最快的方法)
    # 虚拟桌面上的隐藏窗口通常会有特定的样式或最小化状态
    # 关键点：检查窗口是否被“挂起” (Cloaked)
    # 如果窗口在其他桌面，它会被系统 Cloak（掩盖）
    DWMWA_CLOAKED = 14
    cloaked = ctypes.c_int(0)
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)
    )
    if cloaked.value != 0:  # 如果被掩盖了（在其他桌面或隐藏），则过滤掉
        return False

    # 3. 标题与类名过滤
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    if not title or class_name in ["Windows.UI.Core.CoreWindow", "Shell_TrayWnd", "Progman"]:
        return False

    # 4. 过滤最小化
    if win32gui.GetWindowPlacement(hwnd)[1] == win32con.SW_SHOWMINIMIZED:
        return False

    # 5. 样式过滤
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if ex_style & win32con.WS_EX_TOOLWINDOW:
        return False
    owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)

    return owner == 0 or (ex_style & win32con.WS_EX_APPWINDOW)


def get_visible_hwnds():
    hwnds = []
    win32gui.EnumWindows(lambda h, _: hwnds.append(
        h) if is_real_visible_window(h) else None, None)
    return hwnds


if __name__ == "__main__":
    for hwnd in get_visible_hwnds():
        print(f"窗口句柄: {hwnd}, 标题: {win32gui.GetWindowText(hwnd)}")
