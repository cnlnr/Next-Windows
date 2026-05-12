import time
import ctypes
import winreg
import win32gui
import win32api
import win32con

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
    dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_BORDER_COLOR, ctypes.byref(c_color), 4)

def get_target_hwnd():
    """获取鼠标下的顶级窗口"""
    try:
        point = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint(point)
        return win32gui.GetAncestor(hwnd, win32con.GA_ROOT) if hwnd else 0
    except:
        return 0

def main():
    current_hwnd = 0
    DEFAULT_COLOR = 0xFFFFFFFF # 恢复系统默认
    
    print("--- 边框高亮模式（不修改标题栏） ---")
    
    try:
        while True:
            new_hwnd = get_target_hwnd()
            target_color = get_accent_color()

            # 情况 1：鼠标在窗口上
            if new_hwnd != 0:
                # 如果从旧窗口移到新窗口，先还原旧的
                if current_hwnd and new_hwnd != current_hwnd:
                    set_border_color(current_hwnd, DEFAULT_COLOR)
                
                # 检查当前颜色，如果不是主题色（说明被软件重绘覆盖了），则重新应用
                if get_current_border_color(new_hwnd) != target_color:
                    set_border_color(new_hwnd, target_color)
                
                current_hwnd = new_hwnd
                time.sleep(0.05) # 高频检测，对抗重绘
            
            # 情况 2：鼠标在空白处
            else:
                if current_hwnd:
                    set_border_color(current_hwnd, DEFAULT_COLOR)
                    current_hwnd = 0
                time.sleep(0.2)

    except KeyboardInterrupt:
        if current_hwnd:
            set_border_color(current_hwnd, DEFAULT_COLOR)
        print("\n已退出")

if __name__ == '__main__':
    main()