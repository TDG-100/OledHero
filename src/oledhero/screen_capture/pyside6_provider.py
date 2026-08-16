from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication

from oledhero.screen_capture.provider import Screenshot
import time


class PySide6ScreenCapture(QObject):
    def __init__(self) -> None:

        pass

    def request_screenshots(self) -> list[Screenshot]:

        # only spawn application if necessary (try to use existing one)
        application = QGuiApplication.instance()
        if application is None or not hasattr(application, "screens"):
            application = QGuiApplication([])

        qt_screens = application.screens()

        now = time.monotonic_ns()
        qt_images = [screen.grabWindow(0).toImage() for screen in qt_screens]

        screenshots = [Screenshot(image=img, timestamp_ns=now) for img in qt_images]

        return screenshots
