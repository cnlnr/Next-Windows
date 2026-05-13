from next_windows.拖动窗口时透明.window_transparency import WindowTransparency, if_transparent
from next_windows.拖动窗口时透明.wait_for_move_event import wait_for_move_event

# 创建透明度控制器实例
# target_alpha: 拖动时的透明度 (0-255，越小越透明)
# restore_alpha: 恢复后的透明度 (255为完全不透明)
# interval: 动画帧间隔，越小越平滑
transparency_ctrl = WindowTransparency(
    target_alpha=235,    # 拖动时半透明
    restore_alpha=255,   # 恢复完全不透明
    interval=0.005       # 流畅的动画过渡
)


"""主循环：监听窗口拖动事件并控制透明度"""
print("监听窗口拖动事件... (按 Ctrl+C 退出)")

# 记录当前正在处理的句柄，防止冲突
active_hwnd = None

try:
    while True:
        # 阻塞等待拖动事件
        is_start, hwnd = wait_for_move_event()

        if not hwnd or hwnd == 0:
            continue

        if is_start:
            # 记录当前句柄
            active_hwnd = hwnd
            print(f"窗口 {hwnd} 开始拖动...")
            # 建议在这里也判断一下，如果已经透明了就不再触发动画
            transparency_ctrl.set_transparent(hwnd)
        else:
            # 结束拖动
            print(f"窗口 {hwnd} 拖动结束...")
            # 逻辑优化：确保是之前那个窗口，且处于透明状态才恢复
            if if_transparent(hwnd):
                transparency_ctrl.restore(hwnd)
            active_hwnd = None

except KeyboardInterrupt:
    print("\n用户中断，正在退出...")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 最后的仁慈：如果退出时还有窗口被扣在手里，尝试恢复它
    if active_hwnd and if_transparent(active_hwnd):
        transparency_ctrl.restore(active_hwnd)
    print("已退出监听")
