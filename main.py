"""
久坐提醒 - 跳舞小兔子
每25分钟弹出可爱的跳舞兔子提醒起身运动
工作时间：9:00 - 17:00
"""
import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QActionGroup, QWidget
)
from bunny_widget import BunnyWidget


# 配置常量
DEFAULT_REMINDER_MINUTES = 25
DEFAULT_WORK_START = "8:30"
DEFAULT_WORK_END = "18:00"
CHECK_INTERVAL_MS = 30000  # 每30秒检查一次

# 工作时间预设
WORK_START_PRESETS = [
    "8:30", "9:00", "9:30", "10:00",
]
WORK_END_PRESETS = [
    "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00",
]

# 覆盖全屏速度预设（名称, 总秒数）
FULLSCREEN_SPEED_PRESETS = [
    ("极速 (10秒)", 10),
    ("快速 (20秒)", 20),
    ("普通 (40秒)", 40),
    ("慢速 (60秒)", 60),
]
DEFAULT_FULLSCREEN_SECONDS = 20

# 运动时长预设（名称, 分钟数）
EXERCISE_DURATION_PRESETS = [
    ("5 分钟", 5),
    ("10 分钟", 10),
    ("15 分钟", 15),
    ("20 分钟", 20),
]
DEFAULT_EXERCISE_MINUTES = 10
DEFAULT_ESC_EXIT = True
DEFAULT_EXERCISE_PROMPT = "打开抖音肩颈操直播跟练吧~"

# 运动提示语预设
EXERCISE_PROMPT_PRESETS = [
    ("抖音肩颈操直播", "打开抖音肩颈操直播跟练吧~"),
    ("B站健身视频", "打开B站健身视频跟练吧~"),
    ("Keep运动", "打开Keep跟练吧~"),
    ("自由运动", "做做拉伸、跳跳操吧~"),
]

# 提醒间隔预设（名称, 分钟数）
REMINDER_INTERVAL_PRESETS = [
    ("25 分钟", 25),
    ("30 分钟", 30),
    ("35 分钟", 35),
    ("40 分钟", 40),
    ("45 分钟", 45),
]

# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    """加载配置"""
    defaults = {
        "fullscreen_seconds": DEFAULT_FULLSCREEN_SECONDS,
        "exercise_minutes": DEFAULT_EXERCISE_MINUTES,
        "esc_exit": DEFAULT_ESC_EXIT,
        "reminder_minutes": DEFAULT_REMINDER_MINUTES,
        "exercise_prompt": DEFAULT_EXERCISE_PROMPT,
        "work_start": DEFAULT_WORK_START,
        "work_end": DEFAULT_WORK_END,
    }
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            defaults.update(data)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults


def save_config(cfg):
    """保存配置"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class SedentaryReminder:
    """久坐提醒主程序"""

    def __init__(self, app: QApplication):
        self._app = app
        self._bunny_widget = None
        self._last_reminder_time = None
        self._paused = False
        self._config = load_config()

        self._setup_tray()
        self._setup_timer()

        # 记录启动时间作为第一个周期的起点
        if self._is_work_time():
            self._last_reminder_time = datetime.now()

    def _create_tray_icon(self) -> QIcon:
        """生成一个简单的兔子图标"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 兔子头
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(200, 200, 210), 2))
        painter.drawEllipse(12, 20, 40, 36)

        # 耳朵
        painter.drawEllipse(14, 2, 12, 28)
        painter.drawEllipse(38, 2, 12, 28)
        # 内耳
        painter.setBrush(QBrush(QColor(255, 200, 210)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(17, 6, 6, 20)
        painter.drawEllipse(41, 6, 6, 20)

        # 眼睛
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawEllipse(22, 32, 7, 7)
        painter.drawEllipse(35, 32, 7, 7)
        # 高光
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(24, 33, 3, 3)
        painter.drawEllipse(37, 33, 3, 3)

        # 鼻子
        painter.setBrush(QBrush(QColor(255, 182, 193)))
        painter.drawEllipse(29, 39, 6, 5)

        # 脸颊
        painter.setBrush(QBrush(QColor(255, 180, 200, 100)))
        painter.drawEllipse(14, 37, 10, 7)
        painter.drawEllipse(40, 37, 10, 7)

        painter.end()
        return QIcon(pixmap)

    def _setup_tray(self):
        """设置系统托盘"""
        self._tray = QSystemTrayIcon()
        self._tray.setIcon(self._create_tray_icon())
        self._tray.setToolTip("久坐提醒 - 跳舞小兔子")

        menu = QMenu()

        # 立即提醒
        show_action = QAction("立即弹出兔子", menu)
        show_action.triggered.connect(self._show_bunny_now)
        menu.addAction(show_action)

        menu.addSeparator()

        # 覆盖全屏速度 子菜单
        speed_menu = QMenu("覆盖全屏速度", menu)
        speed_group = QActionGroup(speed_menu)
        speed_group.setExclusive(True)

        current_seconds = self._config.get("fullscreen_seconds", DEFAULT_FULLSCREEN_SECONDS)

        for label, seconds in FULLSCREEN_SPEED_PRESETS:
            action = QAction(label, speed_menu, checkable=True)
            action.setData(seconds)
            if seconds == current_seconds:
                action.setChecked(True)
            action.triggered.connect(lambda checked, s=seconds, a=action: self._set_speed(s))
            speed_group.addAction(action)
            speed_menu.addAction(action)

        menu.addMenu(speed_menu)

        # 运动时长 子菜单
        exercise_menu = QMenu("运动时长", menu)
        exercise_group = QActionGroup(exercise_menu)
        exercise_group.setExclusive(True)

        current_exercise = self._config.get("exercise_minutes", DEFAULT_EXERCISE_MINUTES)

        for label, minutes in EXERCISE_DURATION_PRESETS:
            action = QAction(label, exercise_menu, checkable=True)
            action.setData(minutes)
            if minutes == current_exercise:
                action.setChecked(True)
            action.triggered.connect(lambda checked, m=minutes: self._set_exercise_duration(m))
            exercise_group.addAction(action)
            exercise_menu.addAction(action)

        menu.addMenu(exercise_menu)

        # 提醒间隔 子菜单
        interval_menu = QMenu("提醒间隔", menu)
        interval_group = QActionGroup(interval_menu)
        interval_group.setExclusive(True)

        current_interval = self._config.get("reminder_minutes", DEFAULT_REMINDER_MINUTES)

        for label, minutes in REMINDER_INTERVAL_PRESETS:
            action = QAction(label, interval_menu, checkable=True)
            action.setData(minutes)
            if minutes == current_interval:
                action.setChecked(True)
            action.triggered.connect(lambda checked, m=minutes: self._set_reminder_interval(m))
            interval_group.addAction(action)
            interval_menu.addAction(action)

        menu.addMenu(interval_menu)

        # 运动提示语 子菜单
        prompt_menu = QMenu("运动提示语", menu)
        prompt_group = QActionGroup(prompt_menu)
        prompt_group.setExclusive(True)

        current_prompt = self._config.get("exercise_prompt", DEFAULT_EXERCISE_PROMPT)

        for label, prompt in EXERCISE_PROMPT_PRESETS:
            action = QAction(label, prompt_menu, checkable=True)
            action.setData(prompt)
            if prompt == current_prompt:
                action.setChecked(True)
            action.triggered.connect(lambda checked, p=prompt: self._set_exercise_prompt(p))
            prompt_group.addAction(action)
            prompt_menu.addAction(action)

        menu.addMenu(prompt_menu)

        # 工作开始时间 子菜单
        start_menu = QMenu("工作开始时间", menu)
        start_group = QActionGroup(start_menu)
        start_group.setExclusive(True)

        current_start = self._config.get("work_start", DEFAULT_WORK_START)

        for t in WORK_START_PRESETS:
            action = QAction(t, start_menu, checkable=True)
            if t == current_start:
                action.setChecked(True)
            action.triggered.connect(lambda checked, v=t: self._set_work_start(v))
            start_group.addAction(action)
            start_menu.addAction(action)

        menu.addMenu(start_menu)

        # 工作结束时间 子菜单
        end_menu = QMenu("工作结束时间", menu)
        end_group = QActionGroup(end_menu)
        end_group.setExclusive(True)

        current_end = self._config.get("work_end", DEFAULT_WORK_END)

        for t in WORK_END_PRESETS:
            action = QAction(t, end_menu, checkable=True)
            if t == current_end:
                action.setChecked(True)
            action.triggered.connect(lambda checked, v=t: self._set_work_end(v))
            end_group.addAction(action)
            end_menu.addAction(action)

        menu.addMenu(end_menu)

        # Esc退出开关
        self._esc_action = QAction("连按3次Esc可退出", menu, checkable=True)
        self._esc_action.setChecked(self._config.get("esc_exit", DEFAULT_ESC_EXIT))
        self._esc_action.triggered.connect(self._toggle_esc_exit)
        menu.addAction(self._esc_action)

        menu.addSeparator()

        # 暂停/恢复
        self._pause_action = QAction("暂停提醒", menu)
        self._pause_action.triggered.connect(self._toggle_pause)
        menu.addAction(self._pause_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.show()

        # 显示启动通知
        self._tray.showMessage(
            "久坐提醒已启动",
            f"每{current_interval}分钟提醒你起身运动\n"
            f"工作时间：{current_start} - {current_end}\n"
            f"覆盖全屏：{current_seconds}秒",
            QSystemTrayIcon.Information,
            3000
        )

    def _set_speed(self, seconds):
        """设置覆盖全屏速度"""
        self._config["fullscreen_seconds"] = seconds
        save_config(self._config)
        # 找到对应的标签名
        label = next((l for l, s in FULLSCREEN_SPEED_PRESETS if s == seconds), f"{seconds}秒")
        self._tray.showMessage(
            "设置已更新",
            f"覆盖全屏速度：{label}",
            QSystemTrayIcon.Information,
            2000
        )

    def _set_exercise_duration(self, minutes):
        """设置运动时长"""
        self._config["exercise_minutes"] = minutes
        save_config(self._config)
        self._tray.showMessage(
            "设置已更新",
            f"运动时长：{minutes} 分钟",
            QSystemTrayIcon.Information,
            2000
        )

    def _set_exercise_prompt(self, prompt):
        """设置运动提示语"""
        self._config["exercise_prompt"] = prompt
        save_config(self._config)
        self._tray.showMessage(
            "设置已更新",
            f"运动提示语：{prompt}",
            QSystemTrayIcon.Information,
            2000
        )

    def _set_work_start(self, time_str):
        """设置工作开始时间"""
        self._config["work_start"] = time_str
        save_config(self._config)
        end = self._config.get("work_end", DEFAULT_WORK_END)
        self._tray.showMessage(
            "设置已更新",
            f"工作时间：{time_str} - {end}",
            QSystemTrayIcon.Information,
            2000
        )

    def _set_work_end(self, time_str):
        """设置工作结束时间"""
        self._config["work_end"] = time_str
        save_config(self._config)
        start = self._config.get("work_start", DEFAULT_WORK_START)
        self._tray.showMessage(
            "设置已更新",
            f"工作时间：{start} - {time_str}",
            QSystemTrayIcon.Information,
            2000
        )

    def _set_reminder_interval(self, minutes):
        """设置提醒间隔"""
        self._config["reminder_minutes"] = minutes
        save_config(self._config)
        self._tray.showMessage(
            "设置已更新",
            f"提醒间隔：{minutes} 分钟",
            QSystemTrayIcon.Information,
            2000
        )

    def _toggle_esc_exit(self, checked):
        """切换Esc退出开关"""
        self._config["esc_exit"] = checked
        save_config(self._config)
        state = "开启" if checked else "关闭"
        self._tray.showMessage("设置已更新", f"连按3次Esc退出：{state}", QSystemTrayIcon.Information, 2000)

    def _setup_timer(self):
        """设置定时检查器"""
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._check_reminder)
        self._check_timer.start(CHECK_INTERVAL_MS)

    @staticmethod
    def _parse_time(time_str):
        """解析 'H:MM' 格式时间为 (hour, minute)"""
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1])

    def _is_work_time(self) -> bool:
        """当前是否在工作时间内"""
        now = datetime.now()
        now_minutes = now.hour * 60 + now.minute
        start_h, start_m = self._parse_time(self._config.get("work_start", DEFAULT_WORK_START))
        end_h, end_m = self._parse_time(self._config.get("work_end", DEFAULT_WORK_END))
        return start_h * 60 + start_m <= now_minutes < end_h * 60 + end_m

    def _check_reminder(self):
        """定时检查是否需要弹出提醒"""
        if self._paused:
            return

        if not self._is_work_time():
            # 不在工作时间，重置计时
            self._last_reminder_time = None
            return

        # 如果刚进入工作时间，初始化计时起点
        if self._last_reminder_time is None:
            self._last_reminder_time = datetime.now()
            return

        # 如果兔子已经在显示，不要重复弹出
        if self._bunny_widget is not None and self._bunny_widget.isVisible():
            return

        # 检查是否到了提醒时间
        elapsed = datetime.now() - self._last_reminder_time
        interval = self._config.get("reminder_minutes", DEFAULT_REMINDER_MINUTES)
        if elapsed >= timedelta(minutes=interval):
            self._show_bunny()

    def _show_bunny(self):
        """显示跳舞兔子"""
        # 清理旧的
        if self._bunny_widget is not None:
            self._bunny_widget.close()
            self._bunny_widget.deleteLater()

        seconds = self._config.get("fullscreen_seconds", DEFAULT_FULLSCREEN_SECONDS)
        exercise = self._config.get("exercise_minutes", DEFAULT_EXERCISE_MINUTES)
        esc_exit = self._config.get("esc_exit", DEFAULT_ESC_EXIT)
        prompt = self._config.get("exercise_prompt", DEFAULT_EXERCISE_PROMPT)
        self._bunny_widget = BunnyWidget(grow_total_seconds=seconds, exercise_minutes=exercise, esc_exit=esc_exit, exercise_prompt=prompt)
        self._bunny_widget.closed_by_user.connect(self._on_bunny_dismissed)
        self._bunny_widget.show()

    def _show_bunny_now(self):
        """立即显示兔子（菜单操作）"""
        self._show_bunny()

    def _on_bunny_dismissed(self):
        """用户点击了去运动，重置计时器"""
        self._last_reminder_time = datetime.now()
        self._bunny_widget = None

    def _toggle_pause(self):
        """切换暂停状态"""
        self._paused = not self._paused
        if self._paused:
            self._pause_action.setText("恢复提醒")
            self._tray.showMessage("提醒已暂停", "点击恢复提醒", QSystemTrayIcon.Information, 2000)
        else:
            self._pause_action.setText("暂停提醒")
            self._last_reminder_time = datetime.now()
            interval = self._config.get("reminder_minutes", DEFAULT_REMINDER_MINUTES)
            self._tray.showMessage("提醒已恢复", f"每{interval}分钟提醒", QSystemTrayIcon.Information, 2000)

    def _quit(self):
        """退出程序"""
        if self._bunny_widget:
            self._bunny_widget._can_close = True
            self._bunny_widget.close()
        self._tray.hide()
        self._app.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，靠托盘管理

    reminder = SedentaryReminder(app)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
