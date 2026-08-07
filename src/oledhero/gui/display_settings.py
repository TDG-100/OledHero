from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from oledhero.display import Display
from oledhero.gui.widgets.toggle_switch import ToggleSwitch


class DisplaySettings(QFrame):

    def __init__(self, parent: QWidget | None = None, display: Display | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("displaySettings")
        self.setFixedWidth(475)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        self._title = QLabel()
        self._title.setObjectName("displaySettingsTitle")
        title_row.addWidget(self._title)
        title_row.addStretch()
        self._enabled_toggle = ToggleSwitch(self)
        self._enabled_toggle.setObjectName("displayEnabledToggle")
        title_row.addWidget(self._enabled_toggle)
        layout.addLayout(title_row)

        information = QGridLayout()
        information.setHorizontalSpacing(24)
        information.setVerticalSpacing(8)

        information.addWidget(QLabel("Resolution"), 1, 0)
        self._resolution = QLabel()
        self._resolution.setObjectName("displaySettingsValue")
        information.addWidget(self._resolution, 1, 1)
        information.setColumnStretch(1, 1)
        layout.addLayout(information)

        layout.addStretch()

        self.set_display(display)

    def set_display(self, display: Display | None) -> None:
        if display is None:
            self._title.setText("No display selected")
            self._resolution.setText("-")
            self._enabled_toggle.setChecked(False)
            self._enabled_toggle.setEnabled(False)
            self._enabled_toggle.setToolTip("")
            return
        
        self._title.setText(display.name or "Display")
        self._resolution.setText(f"{display.metadata.geometry.width} × {display.metadata.geometry.height}")
        self._enabled_toggle.setChecked(display.compatible)
        self._enabled_toggle.setEnabled(display.compatible)
