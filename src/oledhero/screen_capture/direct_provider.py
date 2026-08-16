import time

from oledhero.display import Display
from oledhero.screen_capture.provider import Screenshot


class DirectScreenshotProvider:
    """Capture directly from a display's screen without caching."""

    def get_screenshot(self, display: Display) -> Screenshot | None:
        try:
            image = display.screen.grab_image()
        except RuntimeError:
            # Qt raises RuntimeError when the wrapped QScreen has been deleted.
            return None

        if image.isNull():
            return None
        return Screenshot(image=image, timestamp_ns=time.monotonic_ns())
