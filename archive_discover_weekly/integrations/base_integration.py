from typing import Any, Dict


class BaseIntegration:
    DEFAULT_SETTINGS: Dict[str, Any] = {}

    def __init__(self, settings: Dict[str, Any]):
        settings.update(
            (k, v) for k, v in self.DEFAULT_SETTINGS.items() if k not in settings
        )
        self.settings = settings

    def send_tracks(self, tracks: Dict[str, Any]):
        """Send tracks."""
        raise NotImplementedError

    def send_error(self, exception: BaseException):
        """Send error."""
        raise NotImplementedError
