from logging import Logger

from sclogging import sclogging_main as scl


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SCLogger(metaclass=Singleton):
    _logger = None

    def __init__(self, *args, **kwargs):
        if not self._logger:
            self._logger = scl.get_logger(*args, **kwargs)

    def get_logger(self) -> Logger:
        """

        Retrieves the logger instance associated with this object.

        Returns:
            Logger: The logger instance used for logging messages.
        """

        return self._logger
