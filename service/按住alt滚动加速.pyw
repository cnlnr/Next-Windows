import ctypes
from ctypes import wintypes
import time

# Win32 常量
SPI_GETWHEELSCROLLLINES = 0x0068
SPI_SETWHEELSCROLLLINES = 0x0069
VK_MENU = 0x12  # Alt 键

user32 = ctypes.windll.user32


def get_sys_scroll_lines():
    """获取当前系统默认的滚动行数"""
    lines = wintypes.UINT()
    user32.SystemParametersInfoW(
        SPI_GETWHEELSCROLLLINES, 0, ctypes.byref(lines), 0)
    return lines.value


def set_sys_scroll_lines(lines_count):
    """设置系统的滚动行数"""
    user32.SystemParametersInfoW(SPI_SETWHEELSCROLLLINES, lines_count, None, 0)


# 1. 备份你电脑当前的默认滚动速度（通常是 3）
DEFAULT_LINES = get_sys_scroll_lines()
ACCEL_LINES = 15  # 按住 Alt 时，滚一下相当于滚 15 行（可自由调节）

print(f"系统当前默认滚动行数: {DEFAULT_LINES}")
print("服务已启动... 侦测中，请试着按住 Alt 并滚动任意窗口（如浏览器、代码编辑器）")

is_accelerated = False

try:
    while True:
        # 2. 持续检测 Alt 键物理状态
        alt_pressed = bool(user32.GetAsyncKeyState(VK_MENU) & 0x8000)

        if alt_pressed and not is_accelerated:
            # 按下 Alt 瞬间，把系统滚动速度飙升
            set_sys_scroll_lines(ACCEL_LINES)
            is_accelerated = True
            print(f"🚀 已临时将滚动行数提升至: {ACCEL_LINES} 行")

        elif not alt_pressed and is_accelerated:
            # 松开 Alt 瞬间，立刻还原系统默认速度
            set_sys_scroll_lines(DEFAULT_LINES)
            is_accelerated = False
            print(f"🔄 已恢复系统默认滚动行数: {DEFAULT_LINES} 行")

        # 适当休眠降低 CPU 占用
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n用户终止程序。")
finally:
    # 3. 确保程序退出时，绝对要把系统速度还原，防止影响正常使用
    set_sys_scroll_lines(DEFAULT_LINES)
    print("安全退出，系统设置已还原。")
