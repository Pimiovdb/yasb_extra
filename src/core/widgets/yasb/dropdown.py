import logging
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMenu, QPushButton, QGridLayout, QWidgetAction
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.dropdown import VALIDATION_SCHEMA

class DropdownMenu(QWidget):
    def __init__(self, items, widths):
        super().__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.populate_grid(items, widths)

    def populate_grid(self, items, widths):
        positions = [(i, j) for i in range(3) for j in range(3)]
        for position, (widget, width) in zip(positions, zip(items, widths)):
            widget.setFixedWidth(width)
            self.layout.addWidget(widget, *position)

class DropdownWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(self, items: dict[str, dict], widths: dict[str, int], update_interval: int, callbacks: dict[str, str]):
        super().__init__(update_interval, class_name="dropdown-widget")

        self._items = items
        self._widths = widths
        self._button = QPushButton("\udb83\ude6f")
        self._button.setProperty('class', 'dropdown-button')
        self._menu = QMenu(self._button)
        self._menu.setProperty('class', 'dropdown-menu-container')

        self._menu.setStyleSheet("""
            QMenu{
                background: transparent;
                border-radius: 5px;
            }
            QMenu::item .widget{
                margin-top: 5px;
                margin-right: 5px;
            }
            QMenu::item .label{
                background: #bdae93;
                color: #242424;
            }
            QMenu::item .label:hover{
                background: #fbf1c7;
            }
            QMenu::item{
            }
        """)
        self._populate_menu()
        self._button.setMenu(self._menu)
        self.widget_layout.addWidget(self._button)
        
        self.register_callback("update_items", self._update_items)
        
        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_items"

        self.start_timer()

    def _populate_menu(self):
        widgets = [self._create_widget_instance(item['widget'], item['options']) for item in self._items.values()]
        widths = [self._widths[widget_name] for widget_name in self._items.keys()]
        menu_widget = DropdownMenu(widgets, widths)
        widget_action = QWidgetAction(self._menu)
        widget_action.setDefaultWidget(menu_widget)
        self._menu.addAction(widget_action)

    def _create_widget_instance(self, widget_name, options):
        widget_mapping = {
            "cpu": "core.widgets.yasb.cpu.CpuWidget",
            "memory": "core.widgets.yasb.memory.MemoryWidget",
            "volume": "core.widgets.yasb.volume.VolumeWidget",
            "battery": "core.widgets.yasb.battery.BatteryWidget",
            "clock": "core.widgets.yasb.clock.ClockWidget",
            "disk": "core.widgets.yasb.disk.DiskWidget",
            "traffic": "core.widgets.yasb.traffic.TrafficWidget",
            "wifi": "core.widgets.yasb.wifi.WifiWidget",
            "active_window": "core.widgets.yasb.active_window.ActiveWindowWidget",
            "ip_info": "core.widgets.yasb.custom.CustomWidget",
            "media_player": "core.widgets.win32.media_player.MediaWidget"
        }

        if widget_name in widget_mapping:
            module_path, class_name = widget_mapping[widget_name].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            widget_class = getattr(module, class_name)
            return widget_class(**options)
        else:
            raise ValueError(f"Unknown widget: {widget_name}")


    def _update_items(self):
        try:
            self._menu.clear()
            self._populate_menu()
        except Exception:
            logging.exception("Failed to update dropdown items")
