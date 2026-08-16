from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QHideEvent, QImage, QMouseEvent, QPainter, QPainterPath, QPen, QPixmap, QShowEvent
from PySide6.QtWidgets import QWidget

from oledhero.display import Display, DisplayManagerProtocol
from oledhero.gui.theme import BORDER_COLOR, MUTED_TEXT_COLOR, PANEL_COLOR, PRIMARY_TEXT_COLOR
from oledhero.screen_capture import ScreenshotProvider


class DisplaySelector(QWidget):
    """
    Show displays as rectangles representing the physical setup with some basic information.
    This is used to allow the user to easily select a display.
    """

    displaySelected = Signal(Display)

    _BACKGROUND_LOGO_OPACITY = 0.35
    _BACKGROUND_LOGO_SCALING = 0.90
    _DISPLAY_MARGIN = 28.0
    _DISPLAY_GAP = 3.0
    _CORNER_RADIUS = 7.0
    _SELECTED_BORDER_COLOR = "#2589ff"
    _PREVIEW_INTERVAL_MS = 2_000

    def __init__(
        self,
        display_manager: DisplayManagerProtocol,
        parent: QWidget | None = None,
        *,
        screenshot_provider: ScreenshotProvider,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("displaySelector")
        self.setMouseTracking(True)
        self.setMinimumWidth(300)

        self._display_manager = display_manager
        self._displays: dict[str, Display] = {}
        self._display_rects: dict[str, QRectF] = {}
        self._selected_display_id: str | None = None
        self._previews: dict[str, QImage] = {}

        self._screenshot_provider = screenshot_provider
        self._preview_timer = QTimer(self)
        self._preview_timer.setInterval(self._PREVIEW_INTERVAL_MS)
        self._preview_timer.setTimerType(Qt.TimerType.CoarseTimer)
        self._preview_timer.timeout.connect(self.refresh_previews)

        logo_path = Path(__file__).parent.parent / "assets" / "OledHero.svg"
        self._background_logo = QPixmap(str(logo_path))
        self._scaled_background_logo: tuple[QSize, QPixmap] | None = None

        self.refresh_displays()

    @property
    def selected_display(self) -> Display | None:
        return self._displays.get(self._selected_display_id, None)

    def refresh_displays(self) -> None:
        self._displays = {display.id: display for display in self._display_manager.list_displays()}
        self._display_rects = {}

        if self._displays and self._selected_display_id not in self._displays:
            self._selected_display_id = next(iter(self._displays.keys()))

        self.update()

    def refresh_previews(self) -> None:
        if not self.isVisible() or not self._displays:
            return

        # scale the images to rectangle pixel size so we dont need to store the whole img in ram
        preview_rects = self._layout_displays(
            QRectF(self.rect()).adjusted(
                self._DISPLAY_MARGIN,
                self._DISPLAY_MARGIN,
                -self._DISPLAY_MARGIN,
                -self._DISPLAY_MARGIN,
            )
        )
        device_pixel_ratio = self.devicePixelRatioF()

        previews: dict[str, QImage] = {}
        for display in self._displays.values():
            screenshot = self._screenshot_provider.get_screenshot(display)
            if screenshot is None:
                continue
            image = screenshot.image

            target_rect = preview_rects[display.id]
            target_size = QSize(
                max(1, round(target_rect.width() * device_pixel_ratio)),
                max(1, round(target_rect.height() * device_pixel_ratio)),
            )
            image = image.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            previews[display.id] = image

        self._previews = previews
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # draw logo background
        logo_bounds = QRectF(self.rect())
        logo_bounds.adjust(
            logo_bounds.width() * (1 - self._BACKGROUND_LOGO_SCALING) / 2,
            logo_bounds.height() * (1 - self._BACKGROUND_LOGO_SCALING) / 2,
            -logo_bounds.width() * (1 - self._BACKGROUND_LOGO_SCALING) / 2,
            -logo_bounds.height() * (1 - self._BACKGROUND_LOGO_SCALING) / 2,
        )
        self._draw_background_logo(painter, logo_bounds)

        # draw display rectangles
        self._draw_displays(
            painter,
            QRectF(self.rect()).adjusted(
                self._DISPLAY_MARGIN,
                self._DISPLAY_MARGIN,
                -self._DISPLAY_MARGIN,
                -self._DISPLAY_MARGIN,
            ),
        )

    def _draw_background_logo(self, painter: QPainter, bounds: QRectF) -> None:
        """Generated: Draw the background logo with reduced opacity."""
        if self._background_logo.isNull():
            return

        if self._scaled_background_logo is None:
            logo_size = self._background_logo.size().scaled(
                bounds.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            device_pixel_ratio = self.devicePixelRatioF()
            render_size = QSize(
                max(1, round(logo_size.width() * device_pixel_ratio)),
                max(1, round(logo_size.height() * device_pixel_ratio)),
            )
            self._scaled_background_logo = (
                logo_size,
                self._background_logo.scaled(
                    render_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )

        logo_size, logo = self._scaled_background_logo
        target = QRectF(0, 0, logo_size.width(), logo_size.height())
        target.moveCenter(bounds.center())
        painter.save()
        painter.setOpacity(self._BACKGROUND_LOGO_OPACITY)
        painter.drawPixmap(target, logo, QRectF(logo.rect()))
        painter.restore()

    def _draw_displays(self, painter: QPainter, bounds: QRectF) -> None:
        if not self._display_rects:
            self._display_rects = self._layout_displays(bounds)

        for idx, display in enumerate(self._displays.values()):
            display_rect = self._display_rects[display.id]
            self._draw_display(painter, display, display_rect, idx + 1)

    def _layout_displays(self, bounds: QRectF) -> dict[str, QRectF]:
        if not self._displays:
            return {}

        # Find overall boundings -> Desktop geometry
        geometries = [display.metadata.geometry for display in self._displays.values()]
        left = min(geometry.x for geometry in geometries)
        top = min(geometry.y for geometry in geometries)
        right = max(geometry.x + geometry.width for geometry in geometries)
        bottom = max(geometry.y + geometry.height for geometry in geometries)
        desktop_width = max(1, right - left)
        desktop_height = max(1, bottom - top)
        scale = min(bounds.width() / desktop_width, bounds.height() / desktop_height)

        arrangement_width = desktop_width * scale
        arrangement_height = desktop_height * scale
        origin_x = bounds.center().x() - arrangement_width / 2
        origin_y = bounds.center().y() - arrangement_height / 2

        # Compute rectangles for each display - add a gap for selection ring
        display_rects: dict[str, QRectF] = {}
        inset = self._DISPLAY_GAP / 2
        for display, geometry in zip(self._displays.values(), geometries, strict=True):
            rect = QRectF(
                origin_x + (geometry.x - left) * scale,
                origin_y + (geometry.y - top) * scale,
                geometry.width * scale,
                geometry.height * scale,
            ).adjusted(inset, inset, -inset, -inset)
            display_rects[display.id] = rect
        return display_rects

    def _draw_display(self, painter: QPainter, display: Display, rect: QRectF, display_number: int) -> None:
        """Generated: Draw the display rectangle and highlight the selected display."""
        radius = min(self._CORNER_RADIUS, rect.width() / 10, rect.height() / 10)
        display_path = QPainterPath()
        display_path.addRoundedRect(rect, radius, radius)

        painter.save()
        painter.setClipPath(display_path)
        painter.fillPath(display_path, QColor(PANEL_COLOR))

        preview = self._previews.get(display.id)
        if preview is not None:
            painter.drawImage(rect, preview)
        else:
            painter.setPen(QColor(MUTED_TEXT_COLOR))
            number_font = painter.font()
            number_font.setPixelSize(max(18, min(56, round(rect.height() * 0.35))))
            number_font.setBold(True)
            painter.setFont(number_font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(display_number))

        strip_height = min(40.0, max(26.0, rect.height() * 0.20))
        strip = QRectF(rect.left(), rect.bottom() - strip_height, rect.width(), strip_height)
        painter.fillRect(strip, QColor(7, 9, 12, 224))
        painter.restore()

        selected = display.id == self._selected_display_id
        border = QPen(QColor(self._SELECTED_BORDER_COLOR if selected else BORDER_COLOR))
        border.setWidthF(3.0 if selected else 1.25)
        painter.setPen(border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(display_path)

        self._draw_display_caption(painter, display, rect, strip_height, display_number)

    def _draw_display_caption(self, painter: QPainter, display: Display, rect: QRectF, strip_height: float, display_number: int) -> None:
        """Generated: Draw the display (edid)-name, number and resolution if space allows."""
        painter.save()
        caption_font = painter.font()
        caption_font.setPixelSize(max(10, min(13, round(strip_height * 0.34))))
        painter.setFont(caption_font)

        padding = max(7.0, min(12.0, rect.width() * 0.025))
        text_top = rect.bottom() - strip_height
        geometry = display.metadata.geometry
        resolution = f"{geometry.width} × {geometry.height}"
        resolution_width = painter.fontMetrics().horizontalAdvance(resolution)
        show_resolution = rect.width() >= resolution_width + 110
        if show_resolution:
            resolution_rect = QRectF(
                rect.right() - padding - resolution_width,
                text_top,
                resolution_width,
                strip_height,
            )
            painter.setPen(QColor(MUTED_TEXT_COLOR))
            painter.drawText(resolution_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, resolution)
            caption_right = resolution_rect.left() - 12
        else:
            caption_right = rect.right() - padding

        display_name = display.name or display.metadata.edid_name or display.metadata.name or f"Display {display_number}"
        caption = f"{display_number}  {display_name}"
        caption_rect = QRectF(
            rect.left() + padding,
            text_top,
            max(0.0, caption_right - rect.left() - padding),
            strip_height,
        )
        caption = painter.fontMetrics().elidedText(caption, Qt.TextElideMode.ElideRight, round(caption_rect.width()))
        painter.setPen(QColor(PRIMARY_TEXT_COLOR))
        painter.drawText(caption_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, caption)
        painter.restore()

    def showEvent(self, event: QShowEvent) -> None:
        # start screenshot provider
        super().showEvent(event)
        self._preview_timer.start()
        QTimer.singleShot(0, self.refresh_previews)

    def hideEvent(self, event: QHideEvent) -> None:
        # stop screenshot provider - save CPU usage
        self._preview_timer.stop()
        super().hideEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # check if user clicked on a display to select it
        if event.button() == Qt.MouseButton.LeftButton:
            for display in self._displays.values():
                display_rect = self._display_rects.get(display.id)
                if display_rect is not None and display_rect.contains(event.position()):
                    if display.id != self._selected_display_id:
                        self._selected_display_id = display.id
                        self.displaySelected.emit(display)
                        self.update()
                    event.accept()
                    return
        super().mousePressEvent(event)
