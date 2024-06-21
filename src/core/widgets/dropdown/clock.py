import re
import pytz
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.clock import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from datetime import datetime, timezone
from tzlocal import get_localzone_name
from itertools import cycle
import logging

class ClockWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, label: str, label_alt: str, update_interval: int, timezones: list[str], callbacks: dict[str, str]):
        super().__init__(update_interval, class_name="dropdown-clock-widget")
        self._timezones = cycle(timezones if timezones else [get_localzone_name()])
        self._label_content = label
        self._label_alt_content = label_alt

        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

        self._show_alt_label = False

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)
        self.register_callback("next_timezone", self._next_timezone)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_label"

        self._label.show()
        self._label_alt.hide()

        self._next_timezone()
        self._update_label()
        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label

        if self._show_alt_label:
            self._label.hide()
            self._label_alt.show()
        else:
            self._label.show()
            self._label_alt.hide()

        self._update_label()

    def _get_clock_info(self) -> dict:
        try:
            # Get the current time in UTC and then convert it to the active timezone
            datetime_now = datetime.now(timezone.utc).astimezone(pytz.timezone(self._active_tz))
            formatted_time = datetime_now.strftime(self._datetime_format)
        except Exception as e:
            logging.exception("Failed to retrieve updated clock info")
            formatted_time = "N/A"
        
        return {
            'formatted_time': formatted_time,
            'timezone': self._active_tz
        }

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label_formatted = active_label_content

        try:
            # Set default datetime format if not already set
            self._datetime_format = '%Y-%m-%d %H:%M:%S'

            clock_info = self._get_clock_info()

            label_options = [
                ("{formatted_time}", clock_info['formatted_time']),
                ("{timezone}", clock_info['timezone']),
            ]

            for fmt_str, value in label_options:
                active_label_formatted = active_label_formatted.replace(fmt_str, str(value))


            active_label.setText(active_label_formatted)
        except Exception as e:
            active_label.setText(active_label_content)
            logging.exception("Failed to retrieve updated clock info: %s", str(e))

    def _next_timezone(self):
        self._active_tz = next(self._timezones)
        self.setToolTip(self._active_tz)
        self._update_label()
