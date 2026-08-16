from PySide6.QtCore import QSignalBlocker, Qt, QTimer, Signal
from PySide6.QtGui import QFocusEvent, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QAbstractSpinBox, QHBoxLayout, QSizePolicy, QSlider, QSpinBox, QWidget


class _CommitSlider(QSlider):
    """A slider that also reports completed keyboard and wheel interactions."""

    interactionFinished = Signal()

    _EDIT_KEYS = (
        Qt.Key.Key_Left,
        Qt.Key.Key_Right,
        Qt.Key.Key_Up,
        Qt.Key.Key_Down,
        Qt.Key.Key_PageUp,
        Qt.Key.Key_PageDown,
        Qt.Key.Key_Home,
        Qt.Key.Key_End,
    )

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # Dragging the handle emits QSlider.sliderReleased. A click in the
        # groove does not on every platform/style, so cover that case here.
        was_slider_down = self.isSliderDown()
        super().mouseReleaseEvent(event)
        if not was_slider_down:
            self.interactionFinished.emit()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        super().keyReleaseEvent(event)
        if event.key() in self._EDIT_KEYS and not event.isAutoRepeat():
            self.interactionFinished.emit()

    def wheelEvent(self, event: QWheelEvent) -> None:
        old_value = self.value()
        super().wheelEvent(event)
        if self.value() != old_value:
            self.interactionFinished.emit()


class _PercentageSpinBox(QSpinBox):
    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.selectAll()
        # Mouse focus is followed by a mouse-release cursor placement. Selecting
        # on the next event-loop pass keeps the whole value selected then too.
        QTimer.singleShot(0, self.selectAll)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if not self.hasFocus():
            event.ignore()
            return
        super().wheelEvent(event)


class PercentageSlider(QWidget):
    """An integer percentage slider with a synchronized text field.

    ``valueChanged`` is emitted for live updates. ``editingFinished`` is emitted
    after a slider gesture or a spin-box edit is complete, making it suitable
    for comparatively expensive work.
    """

    valueChanged = Signal(int)
    editingFinished = Signal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
        single_step: int = 1,
        page_step: int = 10,
    ) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._slider = _CommitSlider(Qt.Orientation.Horizontal, self)
        self._slider.setObjectName("percentageSliderControl")
        self._slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._slider, 1, Qt.AlignmentFlag.AlignVCenter)

        self._spin_box = _PercentageSpinBox(self)
        self._spin_box.setObjectName("percentageSpinBox")
        self._spin_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._spin_box.setFrame(False)
        self._spin_box.setKeyboardTracking(False)
        self._spin_box.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._spin_box.setSuffix(" %")
        self._spin_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._spin_box, 0, Qt.AlignmentFlag.AlignVCenter)

        self.setRange(minimum, maximum)
        self.setSingleStep(single_step)
        self.setPageStep(page_step)
        self.setValue(value)

        self._slider.valueChanged.connect(self._slider_value_changed)
        self._spin_box.valueChanged.connect(self._spin_box_value_changed)
        self._slider.sliderReleased.connect(self._emit_editing_finished)
        self._slider.interactionFinished.connect(self._emit_editing_finished)
        self._spin_box.editingFinished.connect(self._spin_box_editing_finished)

    def minimum(self) -> int:
        return self._slider.minimum()

    def setMinimum(self, minimum: int) -> None:
        self.setRange(minimum, self.maximum())

    def maximum(self) -> int:
        return self._slider.maximum()

    def setMaximum(self, maximum: int) -> None:
        self.setRange(self.minimum(), maximum)

    def setRange(self, minimum: int, maximum: int) -> None:
        old_value = self.value()
        with QSignalBlocker(self._slider), QSignalBlocker(self._spin_box):
            self._slider.setRange(minimum, maximum)
            # Use the slider's effective range so both controls also agree when
            # the requested maximum is smaller than the minimum.
            self._spin_box.setRange(self._slider.minimum(), self._slider.maximum())
            self._spin_box.setValue(self._slider.value())
        if self.value() != old_value:
            self.valueChanged.emit(self.value())

    def value(self) -> int:
        return self._slider.value()

    def setValue(self, value: int) -> None:
        old_value = self.value()
        with QSignalBlocker(self._slider), QSignalBlocker(self._spin_box):
            self._slider.setValue(value)
            self._spin_box.setValue(self._slider.value())
        if self.value() != old_value:
            self.valueChanged.emit(self.value())

    def singleStep(self) -> int:
        return self._slider.singleStep()

    def setSingleStep(self, step: int) -> None:
        self._slider.setSingleStep(step)
        self._spin_box.setSingleStep(step)

    def pageStep(self) -> int:
        return self._slider.pageStep()

    def setPageStep(self, step: int) -> None:
        self._slider.setPageStep(step)

    def slider(self) -> QSlider:
        """Return the contained slider for advanced customization."""

        return self._slider

    def spinBox(self) -> QSpinBox:
        """Return the contained spin box for advanced customization."""

        return self._spin_box

    def _slider_value_changed(self, value: int) -> None:
        with QSignalBlocker(self._spin_box):
            self._spin_box.setValue(value)
        self.valueChanged.emit(value)

    def _spin_box_value_changed(self, value: int) -> None:
        with QSignalBlocker(self._slider):
            self._slider.setValue(value)
        self.valueChanged.emit(value)

    def _spin_box_editing_finished(self) -> None:
        # editingFinished normally follows interpretation, while interpretText
        # also makes this robust when the signal is emitted programmatically.
        self._spin_box.interpretText()
        if self._spin_box.value() != self.value():
            self._spin_box_value_changed(self._spin_box.value())
        self._emit_editing_finished()

    def _emit_editing_finished(self) -> None:
        self.editingFinished.emit(self.value())
