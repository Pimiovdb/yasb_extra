import logging
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QMenu, QPushButton, QListView, QWidgetAction, QGridLayout
from PyQt6.QtGui import QAction, QIcon
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

    def __init__(
            self,
            items: dict[str, str],
            widths: dict[str, int],
            update_interval: int,
            callbacks: dict[str, str]
    ):
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
        widgets = [self._create_widget_instance(widget_name) for widget_name in self._items.values()]
        widths = [self._widths[widget_name] for widget_name in self._items.keys()]
        menu_widget = DropdownMenu(widgets, widths)
        widget_action = QWidgetAction(self._menu)
        widget_action.setDefaultWidget(menu_widget)
        self._menu.addAction(widget_action)

    def _create_widget_instance(self, widget_name):
        if widget_name == "cpu":
            from core.widgets.dropdown.cpu import CpuWidget
            return CpuWidget(
                label="\ue266 CPU:{cpu_percent_total}%",
                label_alt="CPU:{cpu_percent_total}",
                histogram_icons=[
                    '\u2581', '\u2582', '\u2583', '\u2584', '\u2585', '\u2586', '\u2587', '\u2588'
                ],
                histogram_num_columns=5,
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
                update_interval=1000,
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
                update_interval=100,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'exec cmd.exe /c start ms-settings:network'
                }
            )
        elif widget_name == "battery":
            from core.widgets.dropdown.battery import BatteryWidget
            return BatteryWidget(
                label="{icon} Battery:{battery_percent}%",
                label_alt="{icon} {battery_percent}%",
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
                label="Time: {formatted_time} ({timezone})",
                label_alt="{formatted_time}",
                update_interval=1000,
                timezones=['UTC', 'America/New_York', 'Europe/London'],
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "disk":
            from core.widgets.dropdown.disk import DiskWidget
            return DiskWidget(
                label="\udb80\udeca {volume_label}{used_percent}%",
                label_alt="Disk: {used_percent}% used of {total_gb}GB ({free_gb}GB free)",
                volume_label="C:",
                update_interval=10000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "traffic":
            from core.widgets.dropdown.traffic import TrafficWidget
            return TrafficWidget(
                label="Up: {upload_speed} Down: {download_speed}",
                label_alt="{upload_speed}/{download_speed}",
                update_interval=1000,
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "wifi":
            from core.widgets.dropdown.wifi import WifiWidget
            return WifiWidget(
                label="{wifi_icon} :{wifi_name}",
                label_alt="{wifi_strength}% {wifi_name}",
                update_interval=1000,
                wifi_icons=['\uf1eb', '\uf1eb', '\uf1eb', '\uf1eb', '\uf1eb'],  # Example icons
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                }
            )
        elif widget_name == "active_window":
            from core.widgets.dropdown.active_window import ActiveWindowWidget , IGNORED_TITLES, IGNORED_CLASSES, IGNORED_PROCESSES
            return ActiveWindowWidget(
                label="Window: {title} ({process})",
                label_alt="{title}",
                callbacks={
                    'on_left': 'do_nothing',
                    'on_middle': 'do_nothing',
                    'on_right': 'do_nothing'
                },
                label_no_window="No active window",
                ignore_window={
                    'titles': IGNORED_TITLES,
                    'classes': IGNORED_CLASSES,
                    'processes': IGNORED_PROCESSES
                },
                monitor_exclusive=True,
                max_length=30,
                max_length_ellipsis="..."
            )
        else:
            raise ValueError(f"Unknown widget: {widget_name}")

    def _update_items(self):
        try:
            self._menu.clear()
            self._populate_menu()
        except Exception:
            logging.exception("Failed to update dropdown items")
