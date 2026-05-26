import ctypes
from pynput import mouse

# 定义 Windows API 常量
OCR_NORMAL = 32512   # 标准箭头 ID
# OCR_HAND = 32649     # 链接游标（小手） ID (已注释)
SPI_SETCURSORS = 0x0057
SPIF_SENDCHANGE = 0x0002

# 游标文件绝对路径
ARROW_CUR = r"C:\Windows\Cursors\arrow_i.cur"
# LINK_CUR = r"C:\Windows\Cursors\aero_link_i.cur" (已注释)


def change_all_cursors():
    """按下时：替换主箭头"""
    # 替换主游标
    h_arrow = ctypes.windll.user32.LoadCursorFromFileW(ARROW_CUR)
    if h_arrow:
        ctypes.windll.user32.SetSystemCursor(h_arrow, OCR_NORMAL)

    # 替换链接游标（已注释）
    # h_link = ctypes.windll.user32.LoadCursorFromFileW(LINK_CUR)
    # if h_link:
    #     ctypes.windll.user32.SetSystemCursor(h_link, OCR_HAND)


def restore_cursor():
    """松开时：恢复系统所有默认游标"""
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE)


def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        if pressed:
            change_all_cursors()
        else:
            restore_cursor()


if __name__ == "__main__":
    print("【游标控制程序】已启动！当前仅对[主箭头]生效。")
    try:
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\n正在安全退出...")
    finally:
        restore_cursor()
