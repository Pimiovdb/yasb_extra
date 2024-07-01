import logging
from settings import APP_BAR_TITLE
from core.utils.win32.windows import WinEvent
from core.widgets.base import BaseWidget
from core.event_service import EventService
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtWidgets import QLabel
from core.validation.widgets.yasb.active_window import VALIDATION_SCHEMA
from core.utils.win32.utilities import get_hwnd_info, get_foreground_window, get_executable_name


IGNORED_TITLES = ['', ' ']
IGNORED_CLASSES = ['WorkerW']
IGNORED_PROCESSES = ['SearchHost.exe']
IGNORED_YASB_TITLES = [APP_BAR_TITLE]
IGNORED_YASB_CLASSES = [
    'Qt620QWindowIcon',
    'Qt621QWindowIcon',
    'Qt620QWindowToolSaveBits',
    'Qt621QWindowToolSaveBits'
]

class ActiveWindowWidget(BaseWidget):
    foreground_change = pyqtSignal(int, WinEvent)
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            label: str,
            label_alt: str,
            callbacks: dict[str, str],
            label_no_window: str,
            ignore_window: dict[str, list[str]],
            monitor_exclusive: bool,
            max_length: int,
            max_length_ellipsis: str,
            update_interval: int = 1000  # Add update_interval to use with the timer
    ):
        super().__init__(class_name="dropdown-active-window-widget")

        self._win_info = None
        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt
        self._active_label = label
        self._label_no_window = label_no_window
        self._monitor_exclusive = monitor_exclusive
        self._max_length = max_length
        self._max_length_ellipsis = max_length_ellipsis
        self._ignore_window = ignore_window
        self._event_service = EventService()

        self._window_title_text = QLabel()
        self._window_title_text.setProperty("class", "label")
        self._window_title_text.setText(self._label_no_window)
        self.widget_layout.addWidget(self._window_title_text)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_label"

        self._start_timer(update_interval)

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label
        self._active_label = self._label_alt_content if self._show_alt_label else self._label_content
        self._update_text()

    def _get_active_window_info(self) -> dict:
        hwnd = get_foreground_window()
        win_info = get_hwnd_info(hwnd)
        executable_name = get_executable_name(hwnd)  # Retrieve the executable name
        if (not win_info or not hwnd or
                not win_info['title'] or
                win_info['title'] in IGNORED_YASB_TITLES or
                win_info['class_name'] in IGNORED_YASB_CLASSES):
            return {
                'title': 'N/A',
                'process': 'N/A',
                'class_name': 'N/A',
                'executable': 'N/A'
            }

        if self._monitor_exclusive and self.screen().name() != win_info['monitor_info'].get('device', None):
            return {
                'title': 'N/A',
                'process': 'N/A',
                'class_name': 'N/A',
                'executable': 'N/A'
            }

        if self._max_length and len(win_info['title']) > self._max_length:
            win_info['title'] = f"{win_info['title'][:self._max_length]}{self._max_length_ellipsis}"

        win_info['executable'] = executable_name  # Add the executable name to the window info

        return win_info

    def _update_label(self):
        try:
            active_window_info = self._get_active_window_info()

            label_options = [
                ("{title}", active_window_info['title']),
                ("{process}", active_window_info['process']),
                ("{class_name}", active_window_info['class_name']),
                ("{executable}", active_window_info['executable']),  # Add the executable label option
            ]

            active_label_formatted = self._active_label
            for fmt_str, value in label_options:
                active_label_formatted = active_label_formatted.replace(fmt_str, str(value))

            self._window_title_text.setText(active_label_formatted)
        except Exception:
            self._window_title_text.setText(self._active_label)
            logging.exception("Failed to retrieve updated active window info")

    def _update_text(self):
        self._update_label()

    def _start_timer(self, update_interval: int):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_text)
        self.timer.start(update_interval)
