import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.battery import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
import logging

class BatteryWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, label: str, label_alt: str, update_interval: int, callbacks: dict[str, str], 
                 time_remaining_natural: bool, charging_options: dict, status_thresholds: dict, status_icons: dict):
        super().__init__(update_interval, class_name="battery-widget")
        self._label_content = label
        self._label_alt_content = label_alt
        self._time_remaining_natural = time_remaining_natural
        self._charging_options = charging_options
        self._status_thresholds = status_thresholds
        self._status_icons = status_icons

        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

        self._show_alt_label = False

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
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

    def _get_battery_info(self) -> dict:
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                'percent': 'N/A',
                'secsleft': 'N/A',
                'power_plugged': 'N/A',
                'icon': self._status_icons['icon_critical']
            }
        
        percent = battery.percent
        if battery.power_plugged:
            icon = self._status_icons['icon_charging']
        elif percent <= self._status_thresholds['critical']:
            icon = self._status_icons['icon_critical']
        elif percent <= self._status_thresholds['low']:
            icon = self._status_icons['icon_low']
        elif percent <= self._status_thresholds['medium']:
            icon = self._status_icons['icon_medium']
        elif percent <= self._status_thresholds['high']:
            icon = self._status_icons['icon_high']
        else:
            icon = self._status_icons['icon_full']

        return {
            'percent': percent,
            'secsleft': battery.secsleft,
            'power_plugged': battery.power_plugged,
            'icon': icon
        }

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label_formatted = active_label_content

        try:
            battery_info = self._get_battery_info()

            label_options = [
                ("{battery_percent}", battery_info['percent']),
                ("{battery_secsleft}", battery_info['secsleft']),
                ("{battery_power_plugged}", battery_info['power_plugged']),
                ("{icon}", battery_info['icon']),
            ]

            for fmt_str, value in label_options:
                active_label_formatted = active_label_formatted.replace(fmt_str, str(value))

            active_label.setText(active_label_formatted)
        except Exception:
            active_label.setText(active_label_content)
            logging.exception("Failed to retrieve updated battery info")
