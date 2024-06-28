import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.wifi import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
import os
import logging

class WifiWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, label: str, label_alt: str, update_interval: int, wifi_icons: list[str], callbacks: dict[str, str]):
        super().__init__(update_interval, class_name="dropdown-wifi-widget")
        self._wifi_icons = wifi_icons

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

    def _get_wifi_info(self) -> dict:
        wifi_icon, strength = self._get_wifi_icon()
        wifi_name = self._get_wifi_name()

        return {
            'wifi_icon': wifi_icon,
            'wifi_name': wifi_name,
            'wifi_strength': strength
        }

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content
        active_label_formatted = active_label_content

        try:
            wifi_info = self._get_wifi_info()

            label_options = [
                ("{wifi_icon}", wifi_info['wifi_icon']),
                ("{wifi_name}", wifi_info['wifi_name']),
                ("{wifi_strength}", wifi_info['wifi_strength']),
            ]

            for fmt_str, value in label_options:
                active_label_formatted = active_label_formatted.replace(fmt_str, str(value))

            active_label.setText(active_label_formatted)
        except Exception:
            active_label.setText(active_label_content)
            logging.exception("Failed to retrieve updated wifi info")

    def _get_wifi_strength(self):
        # Get the wifi strength from the system
        result = os.popen("netsh wlan show interfaces").read()

        # Return 0 if no wifi interface is found
        if "There is no wireless interface on the system." in result:
            return 0

        # Extract signal strength from the result
        for line in result.split("\n"):
            if "Signal" in line:  # FIXME: This will break if the system language is not English
                strength = line.split(":")[1].strip().split(" ")[0].replace("%", "")
                return int(strength)

        return 0

    def _get_wifi_name(self):
        result = os.popen("netsh wlan show interfaces").read()

        for line in result.split("\n"):
            if "SSID" in line:
                return line.split(":")[1].strip()

        return "No WiFi"

    def _get_wifi_icon(self):
        # Map strength to its corresponding icon
        strength = self._get_wifi_strength()

        if strength == 0:
            return self._wifi_icons[0], strength
        elif strength <= 25:
            return self._wifi_icons[1], strength
        elif strength <= 50:
            return self._wifi_icons[2], strength
        elif strength <= 75:
            return self._wifi_icons[3], strength
        else:
            return self._wifi_icons[4], strength
