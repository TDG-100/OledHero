from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget

from oledhero.config import DisplayConfig, app_config, save_app_config
from oledhero.display import Display, DisplayManagerProtocol
from oledhero.display_controller.controller_provider import DDCCIUnsupportedError
from oledhero.gui.widgets.percentage_slider import PercentageSlider
from oledhero.gui.widgets.toggle_switch import ToggleSwitch


class DisplaySettings(QFrame):
    def __init__(
        self,
        parent: QWidget | None = None,
        display: Display | None = None,
        *,
        display_manager: DisplayManagerProtocol,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("displaySettings")
        self.setFixedWidth(475)
        self._display_manager = display_manager
        self._display: Display | None = None
        self._committed_brightness = DisplayConfig().brightness_default_value

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

        information.addWidget(QLabel("Default brightness"), 2, 0)
        self._default_brightness = PercentageSlider(
            self,
            minimum=0,
            maximum=100,
            value=100,
            single_step=1,
            page_step=5,
        )
        self._default_brightness.setObjectName("defaultBrightnessSlider")
        self._default_brightness.editingFinished.connect(self._commit_default_brightness)
        information.addWidget(self._default_brightness, 2, 1)

        information.setColumnStretch(1, 1)
        layout.addLayout(information)

        layout.addStretch()

        self.set_display(display)

    def set_display(self, display: Display | None) -> None:
        self._display = display
        if display is None:
            self._title.setText("No display selected")
            self._resolution.setText("-")
            self._enabled_toggle.setChecked(False)
            self._enabled_toggle.setEnabled(False)
            self._enabled_toggle.setToolTip("")
            self._committed_brightness = DisplayConfig().brightness_default_value
            self._default_brightness.setValue(self._committed_brightness)
            self._default_brightness.setEnabled(False)
            return

        self._title.setText(display.name or "Display")
        self._resolution.setText(f"{display.metadata.geometry.width} × {display.metadata.geometry.height}")
        self._enabled_toggle.setChecked(display.compatible)
        self._enabled_toggle.setEnabled(display.compatible)
        display_config = app_config.displays.get(display.id)
        if display_config is not None:
            self._committed_brightness = display_config.brightness_default_value
        elif display.brightness is not None:
            self._committed_brightness = display.brightness
        else:
            self._committed_brightness = DisplayConfig().brightness_default_value
        self._default_brightness.setValue(self._committed_brightness)
        self._default_brightness.setEnabled(display.compatible)

    def _commit_default_brightness(self, brightness: int) -> None:
        display = self._display
        if display is None or not display.compatible:
            return

        try:
            self._display_manager.set_brightness(display.id, brightness)
        except DDCCIUnsupportedError as error:
            self._default_brightness.setValue(self._committed_brightness)
            QMessageBox.warning(
                self,
                "Brightness update failed",
                f"Could not set brightness for {display.name}: {error}",
            )
            return

        app_config.displays[display.id] = DisplayConfig(brightness_default_value=brightness)
        self._committed_brightness = brightness
        save_app_config()
