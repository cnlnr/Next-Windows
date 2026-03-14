from next_windows.窗口区域扩展.get_all_hwnd import get_visible_hwnds
import win32gui
import win32con

def move(offset_x):
    # 1. 获取全量句柄
    hwnds = get_visible_hwnds()
    
    for hwnd in hwnds:
        try:
            # 2. 获取当前位置 (left, top, right, bottom)
            rect = win32gui.GetWindowRect(hwnd)
            
            # 3. 计算新位置：当前 X + 偏移量
            new_x = rect[0] + offset_x
            new_y = rect[1] # Y 轴保持不变
            
            # 4. 设置位置 (SWP_NOSIZE 保持大小, SWP_NOACTIVATE 不抢焦点)
            win32gui.SetWindowPos(
                hwnd, 0, new_x, new_y, 0, 0, 
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
        except:
            # 某些系统核心窗口拒绝访问时直接跳过
            continue

# 重置窗口位置的函数（可选）
def reset():
    hwnds = get_visible_hwnds()
    for hwnd in hwnds:
        try:
            # 获取当前位置
            rect = win32gui.GetWindowRect(hwnd)
            # 计算新位置：重置到初始位置（假设初始位置是屏幕左侧）
            new_x = 0
            new_y = rect[1] # Y 轴保持不变
            
            # 设置位置
            win32gui.SetWindowPos(
                hwnd, 0, new_x, new_y, 0, 0, 
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
        except:
            continue

if __name__ == "__main__":
    # 向右移动 3000px 输入 3000
    # 向左移动 3000px 输入 -3000
    import time
    for i in range(100):
        move(10) # 每次移动 30px
        time.sleep(0.01) # 每次移动后等待 10ms
    for i in range(100):
        move(-10) # 每次移动 30px
        time.sleep(0.01) # 每次移动后等待 10ms
    reset()
    print("移动操作已完成")
