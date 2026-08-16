from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
)


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._position = 0.0

        self._checked_color = QColor("#218739")
        self._unchecked_color = QColor("#555555")
        self._handle_color = QColor("#F5F5F5")
        self._disabled_color = QColor("#444444")
        self._disabled_handle_color = QColor("#AAAAAA")

        self._animation = QPropertyAnimation(self, b"position", self)
        self._animation.setDuration(140)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.toggled.connect(self._animate)

    @Property(float)
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value: float) -> None:
        self._position = value
        self.update()

    @Property(QColor)
    def checkedColor(self) -> QColor:
        return self._checked_color

    @checkedColor.setter
    def checkedColor(self, color: QColor) -> None:
        self._checked_color = color
        self.update()

    @Property(QColor)
    def uncheckedColor(self) -> QColor:
        return self._unchecked_color

    @uncheckedColor.setter
    def uncheckedColor(self, color: QColor) -> None:
        self._unchecked_color = color
        self.update()

    @Property(QColor)
    def handleColor(self) -> QColor:
        return self._handle_color

    @handleColor.setter
    def handleColor(self, color: QColor) -> None:
        self._handle_color = color
        self.update()

    @Property(QColor)
    def disabledColor(self) -> QColor:
        return self._disabled_color

    @disabledColor.setter
    def disabledColor(self, color: QColor) -> None:
        self._disabled_color = color
        self.update()

    @Property(QColor)
    def disabledHandleColor(self) -> QColor:
        return self._disabled_handle_color

    @disabledHandleColor.setter
    def disabledHandleColor(self, color: QColor) -> None:
        self._disabled_handle_color = color
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(42, 20)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def _animate(self, checked: bool) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    def showEvent(self, event) -> None:
        self._position = 1.0 if self.isChecked() else 0.0
        super().showEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        width = self.width()
        height = self.height()

        if self.isEnabled():
            border_color = self._checked_color if self.isChecked() else self._unchecked_color
            handle_color = self._handle_color
        else:
            border_color = self._disabled_color
            handle_color = self._disabled_handle_color

        # Border
        painter.setBrush(border_color)
        painter.drawRoundedRect(
            0,
            0,
            width,
            height,
            height / 2,
            height / 2,
        )

        # Handle
        margin = 2
        diameter = height - 2 * margin

        left_x = margin
        right_x = width - margin - diameter
        handle_x = left_x + (right_x - left_x) * self._position

        painter.setBrush(handle_color)
        painter.drawEllipse(
            int(handle_x),
            margin,
            diameter,
            diameter,
        )
