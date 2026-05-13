from next_windows.任务栏滚动切换应用 import NextSwitcher


if __name__ == "__main__":
    # 模式选择:
    # "persistent" (对应 Ctrl+Win+Alt+Tab) 扩展屏下可能有bug
    # "standard"   (对应 Alt+Tab)
    # sensitivity: 整数格数触发阈值 (1 代表滚一格换一个)
    # 小技巧：ctrl+w 可以关闭选中的窗口

    app = NextSwitcher(mode="standard", sensitivity=1)
    app.run()
