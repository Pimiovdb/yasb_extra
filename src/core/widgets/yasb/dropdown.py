import logging
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMenu, QPushButton, QListView, QWidgetAction
from PyQt6.QtGui import QAction, QIcon
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.dropdown import VALIDATION_SCHEMA

class DropdownWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
            self,
            items: dict[str, str],
            update_interval: int,
            callbacks: dict[str, str]
    ):
        super().__init__(update_interval, class_name="dropdown-widget")
        
        self._items = items
        self._button = QPushButton("\udb83\ude6f")
        self._button.setProperty('class', 'dropdown-button')
        self._menu = QMenu(self._button)
        self._menu.setProperty('class', 'dropdown-menu-container')

        self._menu.setStyleSheet("""
            QMenu{
                background: transparent;
                border-radius: 5px;
                height: 97;
            }
            QMenu::item .widget{
                margin-top: 5px;
                margin-right: 5px;

            }
            QMenu::item .label{
                background: #bdae93;
                color: #242424;
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
        for name, widget_name in self._items.items():
            widget_instance = self._create_widget_instance(widget_name)
            widget_action = QWidgetAction(self._menu)
            widget_action.setDefaultWidget(widget_instance)
            widget_action.setProperty('class', 'dropdown-menu-widget')
            self._menu.addAction(widget_action)

    def _create_widget_instance(self, widget_name):
        # Correct import paths based on your project structure
        if widget_name == "cpu":
            from core.widgets.dropdown.cpu import CpuWidget
            return CpuWidget(
                label="\ue266 CPU:{info[percent][total]}%",
                label_alt="CPU:{info[histograms][cpu_percent]}",
                histogram_icons=[
                    '\u2581', '\u2582', '\u2583', '\u2584', '\u2585', '\u2586', '\u2587', '\u2588'
                ],
                histogram_num_columns=20,
                update_interval=1000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "memory":
            from core.widgets.dropdown.memory import MemoryWidget
            return MemoryWidget(
                label="\ue266 RAM:{virtual_mem_percent}%",
                label_alt="\ue266 RAM:{virtual_mem_free}",
                update_interval=2000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd /c Taskmgr'
                },
                memory_thresholds={
                    'low': 25,
                    'medium': 50,
                    'high': 90
                }
            )
        elif widget_name == "volume":
            from core.widgets.dropdown.volume import VolumeWidget
            return VolumeWidget(
                label="\uf028 {volume[percent]}",
                label_alt="\uf028 {volume[percent]}",
                update_interval=500,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd.exe /c start ms-settings:network'
                }
            )
        elif widget_name == "battery":
            from core.widgets.dropdown.battery import BatteryWidget
            return BatteryWidget(
                label="\ue266 Battery:{battery[percent]}%",
                label_alt="{percent}%",
                time_remaining_natural=True,
                charging_options={'icon_format': "{charging_icon} {icon}", 'blink_charging_icon': False},
                status_thresholds={'critical': 10, 'low': 25, 'medium': 75, 'high': 95, 'full': 100},
                status_icons={
                    'icon_charging': '\uf0e7',
                    'icon_critical': '\udb80\udc83',
                    'icon_low': '\udb80\udc7a',
                    'icon_medium': '\udb80\udc7c',
                    'icon_high': '\udb80\udc80',
                    'icon_full': '\udb80\udc79'
                },
                update_interval=10000,
                callbacks={'on_left': 'do_nothing', 'on_middle': 'do_nothing', 'on_right': 'do_nothing'}
            )
        elif widget_name == "clock":
            from core.widgets.dropdown.clock import ClockWidget
            return ClockWidget(
                label="{time}",
                label_alt= "{%d-%m-%y %H:%M:%S %Z}",
                timezones= ["Europe/Amsterdam", "America/New_York"],
                update_interval=1000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "disk":
            from core.widgets.dropdown.disk import DiskWidget
            return DiskWidget(
                label="\ue266 Disk:{disk[usage]}%",
                label_alt= "\udb80\udeca {volume_label}{space[used][gb]:.1f}GB / {space[total][gb]:.1f}GB",
                volume_label= "C:",
                update_interval=10000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd.exe /c start ms-settings:storagesense'
                }
            )
        elif widget_name == "traffic":
            from core.widgets.dropdown.traffic import TrafficWidget
            return TrafficWidget(
                label="\uf0ab {network[download_speed]} \uf0aa {network[upload_speed]}",
                label_alt="\uf0ab {network[download_speed]} \uf0aa {network[upload_speed]}",
                update_interval=2000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd.exe /c start ms-settings:network'
                }
            )
        elif widget_name == "wifi":
            from core.widgets.dropdown.wifi import WifiWidget
            return WifiWidget(
                label="\uf1eb {wifi[ssid]}",
                update_interval=5000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd.exe /c start ms-settings:network-wifi'
                }
            )
        elif widget_name == "active_window":
            from core.widgets.dropdown.active_window import ActiveWindowWidget
            return ActiveWindowWidget(
                label="{active_window[title]}",
                update_interval=1000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        else:
            raise ValueError(f"Unknown widget: {widget_name}")

    def _update_items(self):
        try:
            self._menu.clear()
            self._populate_menu()
        except Exception:
            logging.exception("Failed to update dropdown items")
