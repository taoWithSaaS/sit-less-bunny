"""
兔子弹窗组件 - 透明无边框置顶窗口，包含跳舞兔子动画和"去运动啦"按钮
"""
import math
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal, QPoint
)
from PyQt5.QtGui import QPainter, QColor, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QApplication, QGraphicsDropShadowEffect,
    QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
)
import winsound
import ctypes
from bunny_renderer import BunnyRenderer


class BunnyWidget(QWidget):
    """跳舞兔子弹窗"""

    closed_by_user = pyqtSignal()  # 用户点击"去运动啦"时发射

    INITIAL_WIDTH = 320
    INITIAL_HEIGHT = 420
    GROW_STEPS = 4  # 固定4步铺满屏幕
    GROW_FACTOR = 1.65
    ANIMATION_FPS = 12  # 帧率

    def __init__(self, grow_total_seconds=20, exercise_minutes=10, esc_exit=True, exercise_prompt="打开抖音肩颈操直播跟练吧~", parent=None):
        super().__init__(parent)
        self._frame = 0
        self._can_close = True  # 初始可关闭，放大后不可
        self._grow_count = 0
        self._grow_interval_ms = int(grow_total_seconds / self.GROW_STEPS * 1000)
        self._exercise_seconds = exercise_minutes * 60
        self._exercise_remaining = 0
        self._in_exercise_mode = False
        self._esc_exit = esc_exit
        self._esc_count = 0
        self._esc_timer = None
        self._exercise_prompt = exercise_prompt
        self._renderer = BunnyRenderer()

        self._setup_window()
        self._setup_ui()
        self._setup_timers()
        self._position_bottom_left()
        self._start_entrance_animation()

    def _setup_window(self):
        """设置窗口属性：透明、无边框、置顶"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # 不在任务栏显示
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFixedSize(self.INITIAL_WIDTH, self.INITIAL_HEIGHT)

    def _cute_font(self, size=13):
        """获取可爱风格字体，优先使用圆体"""
        candidates = ["站酷快乐体2016修订版", "站酷快乐体", "幼圆", "华文彩云",
                       "Microsoft YaHei UI", "微软雅黑"]
        font_db = QFontDatabase()
        families = font_db.families()
        for name in candidates:
            if name in families:
                font = QFont(name, size)
                font.setBold(True)
                return font
        font = QFont()
        font.setPixelSize(size)
        font.setBold(True)
        return font

    def _setup_ui(self):
        """创建UI：提示文字 + 按钮"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 15)

        # 占位 - 兔子绘制区域
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

        # 提示文字
        self._label = QLabel(f"该去运动啦！\n{self._exercise_prompt}")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setFont(self._cute_font(14))
        self._label.setStyleSheet("""
            QLabel {
                color: #ff6b8a;
                background: transparent;
                padding: 2px;
            }
        """)
        # 文字立体阴影
        label_shadow = QGraphicsDropShadowEffect()
        label_shadow.setBlurRadius(8)
        label_shadow.setColor(QColor(255, 107, 138, 80))
        label_shadow.setOffset(1, 2)
        self._label.setGraphicsEffect(label_shadow)
        layout.addWidget(self._label)

        # 按钮
        self._btn = QPushButton("🏃 去运动啦！")
        self._btn.setCursor(Qt.PointingHandCursor)
        self._btn.setFont(self._cute_font(14))
        self._btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff8fab, stop:0.5 #ff6b8a, stop:1 #e8557a);
                color: white;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 20px;
                padding: 10px 24px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb3c6, stop:0.5 #ff8e9e, stop:1 #ff6b8a);
                border: 2px solid rgba(255,255,255,0.5);
            }
            QPushButton:pressed {
                background: #e55a7a;
                padding-top: 12px;
                padding-bottom: 8px;
            }
        """)
        # 按钮立体阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(255, 80, 120, 140))
        shadow.setOffset(0, 5)
        self._btn.setGraphicsEffect(shadow)
        self._btn.clicked.connect(self._on_go_exercise)
        layout.addWidget(self._btn, alignment=Qt.AlignCenter)

    def _setup_timers(self):
        """设置动画定时器和放大定时器"""
        # 动画帧定时器
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._next_frame)
        self._anim_timer.start(1000 // self.ANIMATION_FPS)

        # 放大定时器
        self._grow_timer = QTimer(self)
        self._grow_timer.timeout.connect(self._grow)
        self._grow_timer.start(self._grow_interval_ms)

    def _position_bottom_left(self):
        """定位到屏幕左下角"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.left() + 30
        y = screen.bottom() - self.height() - 60
        self.move(x, y)

    def _start_entrance_animation(self):
        """弹跳入场动画"""
        screen = QApplication.primaryScreen().geometry()
        start_x = screen.left() + 30
        end_y = screen.bottom() - self.height() - 60
        start_y = screen.bottom() + 10  # 从屏幕底部外弹入

        self.move(start_x, start_y)

        self._entrance_anim = QPropertyAnimation(self, b"geometry")
        self._entrance_anim.setDuration(600)
        self._entrance_anim.setStartValue(QRect(start_x, start_y, self.width(), self.height()))
        self._entrance_anim.setEndValue(QRect(start_x, end_y, self.width(), self.height()))
        self._entrance_anim.setEasingCurve(QEasingCurve.OutBounce)
        self._entrance_anim.start()

    def _start_force_topmost(self):
        """启动强制置顶定时器，防止任务栏抢焦点"""
        if not hasattr(self, '_topmost_timer') or self._topmost_timer is None:
            self._topmost_timer = QTimer(self)
            self._topmost_timer.timeout.connect(self._force_raise)
            self._topmost_timer.start(500)

    def _stop_force_topmost(self):
        """停止强制置顶"""
        if hasattr(self, '_topmost_timer') and self._topmost_timer:
            self._topmost_timer.stop()
            self._topmost_timer = None

    def _force_raise(self):
        """强制窗口置顶"""
        self.raise_()
        self.activateWindow()
        # 调用 Windows API 强制前台
        hwnd = int(self.winId())
        ctypes.windll.user32.SetWindowPos(
            hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002  # HWND_TOPMOST, SWP_NOMOVE | SWP_NOSIZE
        )
        ctypes.windll.user32.SetForegroundWindow(hwnd)

    def _next_frame(self):
        """切换到下一帧动画"""
        self._frame = (self._frame + 1) % self._renderer.TOTAL_FRAMES
        self.update()

    def _grow(self):
        """每10秒放大一次"""
        self._grow_count += 1
        screen = QApplication.primaryScreen().geometry()

        new_w = int(self.width() * self.GROW_FACTOR)
        new_h = int(self.height() * self.GROW_FACTOR)

        # 限制最大为屏幕大小
        new_w = min(new_w, screen.width())
        new_h = min(new_h, screen.height())

        # 3次放大后禁止关闭
        if self._grow_count >= 3:
            self._can_close = False

        # 逐渐向屏幕中心移动
        current_center_x = self.x() + self.width() // 2
        current_center_y = self.y() + self.height() // 2
        screen_center_x = screen.center().x()
        screen_center_y = screen.center().y()

        # 插值移向中心
        lerp = min(self._grow_count * 0.12, 1.0)
        target_cx = int(current_center_x + (screen_center_x - current_center_x) * lerp)
        target_cy = int(current_center_y + (screen_center_y - current_center_y) * lerp)

        new_x = max(screen.left(), target_cx - new_w // 2)
        new_y = max(screen.top(), target_cy - new_h // 2)

        # 确保不超出屏幕
        new_x = min(new_x, screen.right() - new_w)
        new_y = min(new_y, screen.bottom() - new_h)

        # 动画过渡
        self.setFixedSize(new_w, new_h)
        grow_anim = QPropertyAnimation(self, b"geometry")
        grow_anim.setDuration(500)
        grow_anim.setStartValue(self.geometry())
        grow_anim.setEndValue(QRect(new_x, new_y, new_w, new_h))
        grow_anim.setEasingCurve(QEasingCurve.OutCubic)
        grow_anim.start()
        # 保持引用防止GC
        self._current_grow_anim = grow_anim

        # 铺满屏幕后停止放大定时器
        if new_w >= screen.width() and new_h >= screen.height():
            self._grow_timer.stop()
            self._can_close = False
            # 真正全屏，覆盖任务栏
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.Tool |
                Qt.BypassWindowManagerHint  # 绕过窗口管理器，盖住任务栏
            )
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.showFullScreen()
            self.raise_()
            self.activateWindow()
            self._start_force_topmost()

            # 铺满后调整字体大小
            self._label.setFont(self._cute_font(28))
            self._label.setStyleSheet("""
                QLabel {
                    color: #ff6b8a;
                    background: transparent;
                }
            """)
            self._btn.setFont(self._cute_font(24))
            self._btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff8fab, stop:0.5 #ff6b8a, stop:1 #e8557a);
                    color: white;
                    border: 2px solid rgba(255,255,255,0.3);
                    border-radius: 34px;
                    padding: 20px 50px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffb3c6, stop:0.5 #ff8e9e, stop:1 #ff6b8a);
                    border: 2px solid rgba(255,255,255,0.5);
                }
                QPushButton:pressed {
                    background: #e55a7a;
                    padding-top: 22px;
                    padding-bottom: 18px;
                }
            """)

    def _on_go_exercise(self):
        """用户点击去运动 -> 进入运动倒计时模式"""
        self._grow_timer.stop()
        self._in_exercise_mode = True
        self._exercise_remaining = self._exercise_seconds
        self._can_close = False

        # 切换到全屏运动倒计时界面
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self._start_force_topmost()

        # 隐藏按钮，更新文字
        self._btn.hide()
        self._update_exercise_display()

        # 启动倒计时
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._exercise_tick)
        self._countdown_timer.start(1000)

    def _exercise_tick(self):
        """运动倒计时每秒更新"""
        self._exercise_remaining -= 1
        self._update_exercise_display()

        if self._exercise_remaining <= 0:
            self._countdown_timer.stop()
            self._finish_exercise()

    def _update_exercise_display(self):
        """更新倒计时显示"""
        mins = self._exercise_remaining // 60
        secs = self._exercise_remaining % 60
        self._label.setText(f"运动中！别偷懒~\n\n⏱ {mins:02d}:{secs:02d}")
        self._label.setFont(self._cute_font(42))
        self._label.setStyleSheet("""
            QLabel {
                color: #ff6b8a;
                background: transparent;
            }
        """)

    def _finish_exercise(self):
        """运动倒计时结束，显示回来工作按钮"""
        self._in_exercise_mode = False

        # 每3秒循环播放系统提示音，直到用户点击按钮
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        self._beep_timer = QTimer(self)
        self._beep_timer.timeout.connect(lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION))
        self._beep_timer.start(3000)

        # 更新文字提示
        self._label.setText("运动结束！休息得不错~")
        self._label.setFont(self._cute_font(42))
        self._label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                background: transparent;
            }
        """)

        # 显示"我回来工作啦"按钮
        self._btn.setText("💪 我回来工作啦！")
        self._btn.setFont(self._cute_font(24))
        self._btn.disconnect()
        self._btn.clicked.connect(self._on_back_to_work)
        self._btn.show()

    def _on_back_to_work(self):
        """用户点击回来工作，关闭窗口并恢复计时"""
        if hasattr(self, '_beep_timer') and self._beep_timer:
            self._beep_timer.stop()
        self._stop_force_topmost()
        self._can_close = True
        self._anim_timer.stop()
        self.closed_by_user.emit()
        self.close()

    def closeEvent(self, event):
        """拦截关闭事件"""
        if not self._can_close:
            event.ignore()
        else:
            event.accept()

    def keyPressEvent(self, event):
        """拦截Alt+F4等快捷键，支持连按3次Esc强制退出"""
        if event.key() == Qt.Key_Escape and self._esc_exit and not self._can_close:
            self._esc_count += 1
            # 2秒内没连按就重置计数
            if self._esc_timer is not None:
                self._esc_timer.stop()
            self._esc_timer = QTimer(self)
            self._esc_timer.setSingleShot(True)
            self._esc_timer.timeout.connect(self._reset_esc_count)
            self._esc_timer.start(2000)

            if self._esc_count >= 3:
                self._esc_count = 0
                self._force_exit()
            event.ignore()
        elif not self._can_close:
            event.ignore()
        else:
            super().keyPressEvent(event)

    def _reset_esc_count(self):
        """重置Esc计数"""
        self._esc_count = 0

    def _force_exit(self):
        """连按3次Esc强制退出"""
        self._stop_force_topmost()
        self._can_close = True
        self._in_exercise_mode = False
        self._anim_timer.stop()
        self._grow_timer.stop()
        if hasattr(self, '_countdown_timer') and self._countdown_timer:
            self._countdown_timer.stop()
        self.closed_by_user.emit()
        self.close()

    def paintEvent(self, event):
        """绘制兔子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制半透明背景圆角矩形
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

        # 绘制兔子 - 在上方区域
        bunny_area_height = self.height() - 120  # 留出按钮和文字空间
        if bunny_area_height < 50:
            bunny_area_height = self.height() * 2 // 3

        painter.save()
        painter.translate(0, 5)
        self._renderer.render(painter, self.width(), bunny_area_height, self._frame)
        painter.restore()

        painter.end()
