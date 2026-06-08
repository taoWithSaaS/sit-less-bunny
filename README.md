# sit-less-bunny 🐰

一只赖在你屏幕上的跳舞兔子，逼你起身运动。

> 写给程序员和独立开发者——我们都知道久坐的危害，但就是不动。这个工具不跟你讲道理，到点不动它就把你屏幕占满。

## 它干了什么

- 每 **25 分钟**，屏幕左下角蹦出一只摇花球跳舞的白色垂耳兔
- 点击「去运动啦！」进入全屏运动倒计时（默认 10 分钟），倒计时结束才消失
- **不点？** 每隔几秒它就变大一点，直到铺满整个屏幕（包括任务栏），而且关不掉
- 仅在 **9:00 - 17:00** 工作时间运行，不打扰你的摸鱼时间

## 截图

```
  (\(\
  ( -.-)    <- 你不动它就长大
  o_(")(")
```

## 快速开始

```bash
# 1. 克隆
git clone git@github.com:taoWithSaaS/-sit-less-bunny.git
cd sit-less-bunny

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py          # 带控制台（方便调试）
pythonw main.py         # 无控制台（日常使用）
```

启动后在系统托盘（右下角）找到兔子图标，右键菜单可操作。

## 创建桌面快捷方式

Windows 下双击运行：

```bash
cscript create_shortcut.vbs
```

桌面会出现 `SitLessBunny` 快捷方式，双击即可启动，无黑窗口。

## 配置

通过系统托盘右键菜单配置，设置会自动保存到 `config.json`。

| 配置项 | 选项 | 说明 |
|--------|------|------|
| 覆盖全屏速度 | 极速(10s) / 快速(20s) / 普通(40s) / 慢速(60s) | 兔子从出现到铺满全屏的时间 |
| 运动时长 | 5 / 10 / 15 / 20 分钟 | 点击按钮后的全屏倒计时时长，默认 10 分钟 |
| 连按3次Esc可退出 | 开 / 关 | 紧急情况下的后门，2 秒内连按 3 次 Esc 强制退出，默认开启 |

代码中可调的常量（`main.py`）：

```python
REMINDER_INTERVAL_MINUTES = 25   # 提醒间隔（分钟）
WORK_START_HOUR = 9              # 工作开始时间
WORK_END_HOUR = 17               # 工作结束时间
```

## 项目结构

```
├── main.py              # 入口：系统托盘 + 定时器
├── bunny_widget.py      # 弹窗：透明窗口 + 自动放大逻辑
├── bunny_renderer.py    # 渲染：QPainter 绘制兔子 + 烟花花球动画
├── requirements.txt     # PyQt5
├── images/bunny.png     # 图标源图
├── app_icon.ico         # 应用图标
└── create_shortcut.vbs  # Windows 桌面快捷方式生成脚本
```

## 技术栈

- **Python 3.10+**
- **PyQt5** — 透明无边框置顶窗口、QPainter 矢量绘制、QPropertyAnimation 动画
- 无需联网，无后端，纯本地运行

## 为什么不用 Electron / Tauri / ...

因为这就是个提醒工具，不需要 Electron 那种 300MB+ 的运行时。PyQt5 安装约 140MB，运行时内存占用很低——没弹兔子时只有托盘图标和定时器，几乎不消耗资源。

## 已知限制

- 仅测试了 Windows 10/11
- 覆盖全屏后唯一的出路是点那个按钮（这是 feature 不是 bug）

## License

MIT
