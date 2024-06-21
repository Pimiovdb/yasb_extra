import psutil
from humanize import naturalsize
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
import logging

class TrafficWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, label: str, label_alt: str, update_interval: int, callbacks: dict[str, str]):
        super().__init__(update_interval, class_name="dropdown-traffic-widget")
        self.interval = update_interval // 1000

        self._show_alt_label = False
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

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self._label.show()
        self._label_alt.hide()

        self.io = psutil.net_io_counters()
        self.bytes_sent = self.io.bytes_sent
        self.bytes_recv = self.io.bytes_recv

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

    def _get_traffic_info(self) -> dict:
        current_io = psutil.net_io_counters()
        upload_diff = current_io.bytes_sent - self.bytes_sent
        download_diff = current_io.bytes_recv - self.bytes_recv

        if upload_diff < 1024:
            upload_speed = f"{upload_diff} B/s"
        else:
            upload_speed = naturalsize(upload_diff // self.interval) + "/s"

        if download_diff < 1024:
            download_speed = f"{download_diff} B/s"
        else:
            download_speed = naturalsize(download_diff // self.interval) + "/s"

        self.bytes_sent = current_io.bytes_sent
        self.bytes_recv = current_io.bytes_recv

        return {
            'upload_speed': upload_speed,
            'download_speed': download_speed
        }

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label_formatted = active_label_content

        try:
            traffic_info = self._get_traffic_info()

            label_options = [
                ("{upload_speed}", traffic_info['upload_speed']),
                ("{download_speed}", traffic_info['download_speed']),
            ]

            for fmt_str, value in label_options:
                active_label_formatted = active_label_formatted.replace(fmt_str, str(value))

            active_label.setText(active_label_formatted)
        except Exception:
            active_label.setText(active_label_content)
            logging.exception("Failed to retrieve updated traffic info")
