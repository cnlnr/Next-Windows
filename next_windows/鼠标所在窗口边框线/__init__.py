import winreg
import win32gui
import win32api
import win32con
import ctypes
# DWM 属性常量
DWMWA_BORDER_COLOR = 34
dwmapi = ctypes.WinDLL('dwmapi')


def get_accent_color():
    """实时从注册表获取系统主题色 (BGR)"""
    try:
        path = r"Software\Microsoft\Windows\DWM"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            value, _ = winreg.QueryValueEx(key, "AccentColor")
            return value & 0xFFFFFF
    except:
        return 0x0099FF


def get_current_border_color(hwnd):
    """获取窗口当前的边框颜色"""
    color = ctypes.c_int(0)
    dwmapi.DwmGetWindowAttribute(
        hwnd, DWMWA_BORDER_COLOR, ctypes.byref(color), ctypes.sizeof(color)
    )
    return color.value


def set_border_color(hwnd, color):
    """仅设置边框颜色"""
    if not hwnd or not win32gui.IsWindow(hwnd):
        return
    c_color = ctypes.c_int(color)
    dwmapi.DwmSetWindowAttribute(
        hwnd, DWMWA_BORDER_COLOR, ctypes.byref(c_color), 4)


def get_target_hwnd():
    """获取鼠标下的顶级窗口"""
    try:
        point = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint(point)
        return win32gui.GetAncestor(hwnd, win32con.GA_ROOT) if hwnd else 0
    except:
        return 0
