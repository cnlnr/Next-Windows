import ctypes
import os
from pynput import mouse

# 定义常量
OCR_NORMAL = 32512  # 标准箭头游标的 ID
SPI_SETCURSORS = 0x0057
SPIF_SENDCHANGE = 0x0002

# 游标文件路径
CURSOR_PATH = r"C:\Windows\Cursors\arrow_r.cur"


def change_cursor(cursor_path):
    """加载并设置系统游标"""
    hcursor = ctypes.windll.user32.LoadCursorFromFileW(cursor_path)
    if hcursor:
        ctypes.windll.user32.SetSystemCursor(hcursor, OCR_NORMAL)


def restore_cursor():
    """恢复系统默认游标"""
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE)


def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        if pressed:
            print("鼠标按下：更换游标")
            change_cursor(CURSOR_PATH)
        else:
            print("鼠标松开：恢复游标")
            restore_cursor()


# 启动监听
print("程序已运行，按 Ctrl+C 可停止。")
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
