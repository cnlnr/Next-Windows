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

def main():
    """主循环：监听窗口拖动事件并控制透明度"""
    print("监听窗口拖动事件... (按 Ctrl+C 退出)")
    try:
        while True:
            # 阻塞等待拖动事件
            is_start, hwnd = wait_for_move_event()
            
            if hwnd == 0:
                continue
            
            if is_start:
                # 开始拖动 → 设置窗口透明（带动画）
                print(f"窗口 {hwnd} 开始拖动，变为透明...")
                transparency_ctrl.set_transparent(hwnd)
            else:
                # 结束拖动 → 恢复不透明（带动画）
                print(f"窗口 {hwnd} 拖动结束，恢复不透明...")
                if if_transparent(hwnd):
                    transparency_ctrl.restore(hwnd)
    except KeyboardInterrupt:
        print("已退出监听")

if __name__ == "__main__":
    main()