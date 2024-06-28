import os
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.disk import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
import logging

class DiskWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, label: str, label_alt: str, volume_label: str, update_interval: int, callbacks: dict[str, str]):
        super().__init__(update_interval, class_name="dropdown-disk-widget")
        self._label_content = label
        self._label_alt_content = label_alt
        self._volume_label = volume_label

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

    def _get_disk_info(self) -> dict:
        result = os.popen("WMIC LOGICALDISK GET Name,Size,FreeSpace").read()  # WMIC is deprecated, but all other options require elevation
        used_space = 0
        total_space = 0
        for line in result.split("\n"):
            if self._volume_label in line:
                used_space = int(line.split()[0].strip())
                total_space = int(line.split()[2].strip())

        if used_space and total_space:
            return {
                'total_mb': total_space / 1024,
                'total_gb': total_space / 1024**3,
                'used_mb': used_space / 1024,
                'used_gb': used_space / 1024**3,
                'used_percent': (used_space / total_space) * 100,
                'free_mb': (total_space - used_space) / 1024,
                'free_gb': (total_space / 1024**3) - (used_space / 1024**3),
                'free_percent': ((total_space - used_space) / total_space) * 100
            }
        return {
            'total_mb': 'N/A',
            'total_gb': 'N/A',
            'used_mb': 'N/A',
            'used_gb': 'N/A',
            'used_percent': 'N/A',
            'free_mb': 'N/A',
            'free_gb': 'N/A',
            'free_percent': 'N/A'
        }

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label_formatted = active_label_content

        try:
            disk_info = self._get_disk_info()

            label_options = [
                ("{total_mb}", f"{disk_info['total_mb']:.2f}"),
                ("{total_gb}", f"{disk_info['total_gb']:.2f}"),
                ("{used_mb}", f"{disk_info['used_mb']:.2f}"),
                ("{used_gb}", f"{disk_info['used_gb']:.2f}"),
                ("{used_percent}", f"{disk_info['used_percent']:.2f}"),
                ("{free_mb}", f"{disk_info['free_mb']:.2f}"),
                ("{free_gb}", f"{disk_info['free_gb']:.2f}"),
                ("{free_percent}", f"{disk_info['free_percent']:.2f}"),
                ("{volume_label}", self._volume_label)
            ]

            for fmt_str, value in label_options:
                active_label_formatted = active_label_formatted.replace(fmt_str, str(value))

            active_label.setText(active_label_formatted)
        except Exception:
            active_label.setText(active_label_content)
            logging.exception("Failed to retrieve updated disk info")
