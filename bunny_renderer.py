"""
兔子绘制器 - 用QPainter绘制可爱的白色垂耳兔啦啦队动画
"""
import math
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QBrush, QPen, QRadialGradient,
    QLinearGradient, QPainterPath
)


class BunnyRenderer:
    """绘制可爱的白色垂耳兔，支持多帧啦啦队跳舞动画"""

    TOTAL_FRAMES = 12

    # 颜色常量
    WHITE = QColor(255, 255, 255)
    LIGHT_GRAY = QColor(240, 240, 245)
    BODY_SHADOW = QColor(220, 220, 230)
    PINK = QColor(255, 182, 193)
    DEEP_PINK = QColor(255, 105, 140)
    CHEEK_PINK = QColor(255, 160, 180, 150)
    EYE_BLACK = QColor(30, 30, 30)
    EYE_HIGHLIGHT = QColor(255, 255, 255, 220)
    MOUTH_COLOR = QColor(200, 100, 120)

    # 花球颜色
    POM_COLORS = [
        QColor(255, 100, 130),  # 粉红
        QColor(255, 200, 80),   # 金黄
        QColor(130, 210, 255),  # 天蓝
        QColor(180, 130, 255),  # 紫色
        QColor(130, 255, 180),  # 薄荷绿
        QColor(255, 150, 50),   # 橙色
    ]

    def render(self, painter: QPainter, width: int, height: int, frame: int):
        """在给定区域内绘制兔子动画的一帧"""
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # 计算缩放，保持兔子在画布内（设计基准200x280）
        scale_x = width / 200.0
        scale_y = height / 280.0
        scale = min(scale_x, scale_y)

        painter.save()
        painter.translate(width / 2, height / 2)
        painter.scale(scale, scale)
        painter.translate(0, 10)

        t = frame / self.TOTAL_FRAMES
        phase = t * 2 * math.pi

        # 身体弹跳
        bounce_y = math.sin(phase) * 8
        # 身体左右摇摆
        sway_x = math.sin(phase * 0.5) * 5
        # 身体倾斜
        tilt = math.sin(phase) * 5

        painter.translate(sway_x, bounce_y)
        painter.rotate(tilt)

        self._draw_body(painter, frame, phase)
        self._draw_head(painter, frame, phase)
        self._draw_arms_and_poms(painter, frame, phase)
        self._draw_feet(painter, frame, phase)

        painter.restore()

    def _draw_body(self, painter, frame, phase):
        """绘制身体"""
        body_rect = QRectF(-40, -10, 80, 90)
        grad = QRadialGradient(QPointF(-10, 10), 80)
        grad.setColorAt(0, self.WHITE)
        grad.setColorAt(0.7, self.LIGHT_GRAY)
        grad.setColorAt(1, self.BODY_SHADOW)
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(200, 200, 210), 1.5))
        painter.drawEllipse(body_rect)

        # 肚子
        belly_rect = QRectF(-22, 10, 44, 50)
        belly_grad = QRadialGradient(QPointF(0, 35), 30)
        belly_grad.setColorAt(0, QColor(255, 235, 240, 100))
        belly_grad.setColorAt(1, QColor(255, 235, 240, 0))
        painter.setBrush(QBrush(belly_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(belly_rect)

    def _draw_head(self, painter, frame, phase):
        """绘制头部和耳朵"""
        painter.save()
        head_tilt = math.sin(phase + 0.5) * 3
        painter.rotate(head_tilt)

        # 头
        head_rect = QRectF(-35, -75, 70, 70)
        head_grad = QRadialGradient(QPointF(-8, -50), 50)
        head_grad.setColorAt(0, self.WHITE)
        head_grad.setColorAt(0.8, self.LIGHT_GRAY)
        head_grad.setColorAt(1, self.BODY_SHADOW)
        painter.setBrush(QBrush(head_grad))
        painter.setPen(QPen(QColor(200, 200, 210), 1.5))
        painter.drawEllipse(head_rect)

        # 垂耳
        self._draw_ear(painter, -25, -65, phase, left=True)
        self._draw_ear(painter, 25, -65, phase, left=False)

        # 眼睛
        self._draw_eyes(painter, phase)

        # 脸颊红晕
        painter.setBrush(QBrush(self.CHEEK_PINK))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-30, -38, 14, 10))
        painter.drawEllipse(QRectF(16, -38, 14, 10))

        # 嘴巴
        self._draw_mouth(painter, phase)

        # 鼻子
        nose_path = QPainterPath()
        nose_path.moveTo(0, -38)
        nose_path.lineTo(-4, -33)
        nose_path.lineTo(4, -33)
        nose_path.closeSubpath()
        painter.setBrush(QBrush(self.PINK))
        painter.setPen(Qt.NoPen)
        painter.drawPath(nose_path)

        painter.restore()

    def _draw_ear(self, painter, x, y, phase, left):
        """绘制一只垂耳"""
        painter.save()
        ear_swing = math.sin(phase + (0 if left else math.pi)) * 8
        painter.translate(x, y)
        painter.rotate(ear_swing + (30 if left else -30))

        ear_path = QPainterPath()
        ear_path.moveTo(0, 0)
        ear_path.cubicTo(-8, 15, -12, 50, -5, 70)
        ear_path.cubicTo(-2, 75, 6, 75, 8, 70)
        ear_path.cubicTo(14, 50, 10, 15, 0, 0)
        ear_grad = QLinearGradient(QPointF(0, 0), QPointF(0, 70))
        ear_grad.setColorAt(0, self.WHITE)
        ear_grad.setColorAt(1, self.LIGHT_GRAY)
        painter.setBrush(QBrush(ear_grad))
        painter.setPen(QPen(QColor(200, 200, 210), 1.2))
        painter.drawPath(ear_path)

        # 内耳粉色
        inner_path = QPainterPath()
        inner_path.moveTo(0, 8)
        inner_path.cubicTo(-5, 20, -7, 45, -3, 62)
        inner_path.cubicTo(-1, 66, 4, 66, 5, 62)
        inner_path.cubicTo(8, 45, 6, 20, 0, 8)
        painter.setBrush(QBrush(QColor(255, 200, 210, 180)))
        painter.setPen(Qt.NoPen)
        painter.drawPath(inner_path)

        painter.restore()

    def _draw_eyes(self, painter, phase):
        """绘制眼睛"""
        for side in [-1, 1]:
            ex = side * 14
            ey = -48
            painter.setBrush(QBrush(self.WHITE))
            painter.setPen(QPen(QColor(180, 180, 190), 1))
            painter.drawEllipse(QRectF(ex - 8, ey - 8, 16, 16))

            pupil_offset_x = math.sin(phase) * 2
            pupil_offset_y = math.cos(phase) * 1
            painter.setBrush(QBrush(self.EYE_BLACK))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(
                ex - 5 + pupil_offset_x, ey - 5 + pupil_offset_y, 10, 10
            ))
            painter.setBrush(QBrush(self.EYE_HIGHLIGHT))
            painter.drawEllipse(QRectF(ex - 2 + pupil_offset_x, ey - 4 + pupil_offset_y, 5, 5))

    def _draw_mouth(self, painter, phase):
        """绘制嘴巴"""
        smile = 3 + math.sin(phase) * 2
        mouth_path = QPainterPath()
        mouth_path.moveTo(-8, -28)
        mouth_path.cubicTo(-4, -28 + smile, 4, -28 + smile, 8, -28)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.MOUTH_COLOR, 1.8, Qt.SolidLine, Qt.RoundCap))
        painter.drawPath(mouth_path)

    def _draw_arms_and_poms(self, painter, frame, phase):
        """绘制手臂和啦啦队花球"""
        for side in [-1, 1]:
            painter.save()

            if side == -1:
                arm_angle = -60 + math.sin(phase) * 50
            else:
                arm_angle = -60 + math.sin(phase + math.pi) * 50

            arm_x = side * 38
            arm_y = 10

            painter.translate(arm_x, arm_y)
            painter.rotate(side * arm_angle)

            # 手臂
            arm_path = QPainterPath()
            arm_path.moveTo(0, 0)
            arm_path.cubicTo(side * 5, -15, side * 8, -30, side * 5, -45)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(self.BODY_SHADOW, 8, Qt.SolidLine, Qt.RoundCap))
            painter.drawPath(arm_path)
            painter.setPen(QPen(self.WHITE, 6, Qt.SolidLine, Qt.RoundCap))
            painter.drawPath(arm_path)

            # 花球
            pom_x = side * 5
            pom_y = -48
            self._draw_pom(painter, pom_x, pom_y, phase + (0 if side == -1 else math.pi), frame)

            painter.restore()

    def _draw_pom(self, painter, cx, cy, phase, frame):
        """绘制啦啦队花球 - 烟花状丝带向外绽放"""
        # 手柄棒
        painter.setPen(QPen(QColor(180, 160, 140), 3, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(cx, cy + 12), QPointF(cx, cy + 2))

        num_ribbons = 20
        num_layers = 3

        for layer in range(num_layers):
            layer_phase = phase + layer * 0.5
            base_length = 10 + layer * 7
            alpha = 240 - layer * 50

            for i in range(num_ribbons):
                base_angle = (i / num_ribbons) * 2 * math.pi
                wobble = math.sin(layer_phase * 2.5 + i * 1.7) * 0.3
                angle = base_angle + wobble + layer * 0.2

                length = base_length + math.sin(i * 2.3 + layer_phase) * 5

                ex = cx + math.cos(angle) * length
                ey = cy + math.sin(angle) * length

                ctrl_offset = math.sin(layer_phase * 3 + i * 0.9) * 6
                ctrl_x = cx + math.cos(angle) * length * 0.55 + math.cos(angle + 1.57) * ctrl_offset
                ctrl_y = cy + math.sin(angle) * length * 0.55 + math.sin(angle + 1.57) * ctrl_offset

                color_idx = (i + layer) % len(self.POM_COLORS)
                color = QColor(self.POM_COLORS[color_idx])
                brightness = 1.0 + 0.35 * math.sin(layer_phase * 4 + i * 1.3)
                color.setRed(min(255, int(color.red() * brightness)))
                color.setGreen(min(255, int(color.green() * brightness)))
                color.setBlue(min(255, int(color.blue() * brightness)))
                color.setAlpha(alpha)

                pen_width = max(0.8, 2.0 - layer * 0.3)
                painter.setPen(QPen(color, pen_width, Qt.SolidLine, Qt.RoundCap))
                painter.setBrush(Qt.NoBrush)

                ribbon = QPainterPath()
                ribbon.moveTo(cx, cy)
                ribbon.quadTo(QPointF(ctrl_x, ctrl_y), QPointF(ex, ey))
                painter.drawPath(ribbon)

                # 末端火星亮点
                if (i + frame) % 3 == 0:
                    spark_bright = min(1.0, brightness)
                    spark_color = QColor(255, 255, 220, int(200 * spark_bright))
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(spark_color))
                    spark_size = 1.5 + math.sin(layer_phase + i) * 0.8
                    painter.drawEllipse(QPointF(ex, ey), spark_size, spark_size)

        # 中心金色圆
        painter.setPen(QPen(QColor(220, 190, 100), 1.5))
        painter.setBrush(QBrush(QColor(255, 230, 130)))
        painter.drawEllipse(QPointF(cx, cy), 4, 4)

    def _draw_feet(self, painter, frame, phase):
        """绘制脚"""
        for side in [-1, 1]:
            foot_x = side * 20
            if side == -1:
                foot_y = 82 + math.sin(phase) * 5
            else:
                foot_y = 82 + math.sin(phase + math.pi) * 5

            foot_grad = QRadialGradient(QPointF(foot_x, foot_y), 15)
            foot_grad.setColorAt(0, self.WHITE)
            foot_grad.setColorAt(1, self.BODY_SHADOW)
            painter.setBrush(QBrush(foot_grad))
            painter.setPen(QPen(QColor(200, 200, 210), 1))
            painter.drawEllipse(QRectF(foot_x - 14, foot_y - 8, 28, 18))

            painter.setBrush(QBrush(QColor(255, 200, 210, 120)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(foot_x - 6, foot_y - 3, 12, 10))
