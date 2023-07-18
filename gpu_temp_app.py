# gpu_temp_app.py

# GPU Temperature Monitor Application
# Created by Swoots

import sys
import pynvml
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget, QMenu, QAction, qApp, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QPen
from PyQt5.QtCore import QTimer, Qt, QByteArray
import winsound
import configparser
from config import GRADIENT_POINTS, GRADIENT_COLORS, HOTSPOT_OFFSET, TEMPERATURE_UPDATE_INTERVAL, WINDOW_RECT, POSITION, WARNING_TEMPERATURE

gradient_points = GRADIENT_POINTS
gradient_colors = GRADIENT_COLORS

class TransparentClock(QWidget):
    def __init__(self):
        super().__init__()
        self.gpu_handle = None
        self.blink_flag = False
        self.text_font = 'Courier New'
        self.temp_unit = 'C'  # Default temperature unit is Celsius
        self.initUI()

    def initUI(self):
        self.window_width = WINDOW_RECT['width']
        self.window_height = WINDOW_RECT['height']
        self.is_move_resize_enabled = False
        self.is_warning_enabled = False
        
        self.background_color = QColor(0, 0, 0, 200)

        self.setWindowTitle('GPU Temperature')
        self.setGeometry(0, 0, self.window_width, self.window_height)

        # Set window flags to enable transparency and disable window frame
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.temperature_label = QLabel(self)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setStyleSheet("QLabel { font: 24pt 'Courier New', monospace; }")  # Set the font using CSS
        self.temperature_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow resizing through the widget

        # Initialize NVML to get GPU temperature
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count > 0:
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        # Update the temperature label every second (1000ms) by default
        temperature_update_timer = QTimer(self)
        temperature_update_timer.timeout.connect(self.update_temperature)
        temperature_update_timer.start(TEMPERATURE_UPDATE_INTERVAL)

        self.position_at_top_right_corner()

    def position_at_top_right_corner(self):
        screen_geo = QDesktopWidget().availableGeometry(self)
        self.move((screen_geo.width() - self.window_width) - POSITION['x'], (self.height() - POSITION['y']))

    def resizeEvent(self, event):
        self.window_width = self.width()
        self.window_height = self.height()
        self.temperature_label.setGeometry(self.rect())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set semi-transparent background when move/resize is enabled
        if self.is_move_resize_enabled:
            painter.fillRect(self.rect(), self.background_color)
            painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
            painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_move_resize_enabled:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_move_resize_enabled:
            # Check if the mouse is close to the edges of the window
            # within a certain range (e.g., 20 pixels)
            edge_distance = 20
            cursor_pos = event.pos()
            window_rect = self.rect()
            window_width = window_rect.width()
            window_height = window_rect.height()

            right_edge = cursor_pos.x() >= window_width - edge_distance
            bottom_edge = cursor_pos.y() >= window_height - edge_distance

            # Set the cursor shape for resizing based on the edge position
            if right_edge and bottom_edge:
                self.setCursor(Qt.SizeFDiagCursor)
            elif right_edge:
                self.setCursor(Qt.SizeHorCursor)
            elif bottom_edge:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

            if event.buttons() == Qt.LeftButton:
                # Resize the window based on the cursor position
                if right_edge:
                    new_width = max(cursor_pos.x(), 200)  # Lower limit on window_width is 200px
                    if new_width / window_height < 4:
                        new_width = window_height * 4
                    self.resize(new_width, window_height)
                if bottom_edge:
                    new_height = max(cursor_pos.y(), 50)  # Lower limit on window_height is 50px
                    new_width = window_width
                    if window_width / new_height < 4:
                        new_width = new_height * 4
                    self.resize(new_width, new_height)

                # Move the window if not close to the edges
                if not (right_edge or bottom_edge):
                    self.setCursor(Qt.SizeAllCursor)
                    self.move(event.globalPos() - self.drag_position)

            event.accept()

    def mouseDoubleClickEvent(self, event):
        if self.is_move_resize_enabled:
            self.setWindowState(self.windowState() ^ Qt.WindowMaximized)
            event.accept()

    def update_temperature(self):
        if self.gpu_handle:
            temperature = self.get_gpu_temperature()
            
            if self.temp_unit == 'F':
                displayed_temperature = round(temperature * 9 / 5 + 32)
            elif self.temp_unit == 'K':
                displayed_temperature = temperature + 273
            else:
                displayed_temperature = temperature

            if self.blink_flag:
                degree_symbol = "°"
            else:
                if temperature >= WARNING_TEMPERATURE and self.is_warning_enabled:
                    winsound.Beep(750, 100)  # Frequency: 750Hz, Duration: 100ms
                degree_symbol = " "

            lower_point = max([point for point in gradient_points if point <= temperature])
            upper_point = min([point for point in gradient_points if point >= temperature])

            if lower_point == upper_point:
                ratio = 0
            else:
                ratio = (temperature - lower_point) / (upper_point - lower_point)

            color = self.interpolate_color(gradient_colors[gradient_points.index(lower_point)], gradient_colors[gradient_points.index(upper_point)], ratio)

            color_string = f'rgb({color[0]}, {color[1]}, {color[2]})'
            self.temperature_label.setStyleSheet(f'QLabel {{ color: {color_string}; font: {round(self.window_height * 0.64)}px {self.text_font}, monospace, bold;}}')
            self.temperature_label.setText(f"GPU: {displayed_temperature}{degree_symbol}{self.temp_unit}")
            self.blink_flag = not self.blink_flag  # Toggle blinking

    def get_gpu_temperature(self):
        temperature = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
        # HotSpot offset (Example value, please refer to your GPU specifications)
        if temperature <= 45:
            hotspot_offset = HOTSPOT_OFFSET['low']
        elif temperature >= 65:
            hotspot_offset = HOTSPOT_OFFSET['high']
        else:
            hotspot_offset = round(HOTSPOT_OFFSET['low'] + (temperature - 45) * (HOTSPOT_OFFSET['high'] - HOTSPOT_OFFSET['low']) / (65 - 45))

        return temperature + hotspot_offset

    def interpolate_color(self, color1, color2, ratio):
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = round(r1 + (r2 - r1) * ratio)
        g = round(g1 + (g2 - g1) * ratio)
        b = round(b1 + (b2 - b1) * ratio)
        return r, g, b

    def save_settings(self):
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'width': str(clock.window_width),
            'height': str(clock.window_height),
            'x_pos': str(clock.pos().x()),
            'y_pos': str(clock.pos().y()),
            'font': clock.text_font,
            'temp_unit': clock.temp_unit,
        }

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def closeEvent(self):
        # Clean up NVML before closing the application
        self.save_settings()
        pynvml.nvmlShutdown()
        app.quit()

def restore_size():
    # Restore the initial size of the window
    clock.resize(WINDOW_RECT['width'], WINDOW_RECT['height'])

def restore_position():
    # Restore the position size of the window
    screen_geo = QDesktopWidget().availableGeometry(clock)
    clock.move((screen_geo.width() - clock.window_width) - POSITION['x'], (clock.height() - POSITION['y']))

def toggle_move_resize():
    clock.is_move_resize_enabled = not clock.is_move_resize_enabled
    toggle_move_resize_action.setChecked(True) if clock.is_move_resize_enabled else toggle_move_resize_action.setChecked(False)

def toggle_visibility():
    global is_clock_displayed
    if not is_clock_displayed:
        clock.show()
        toggle_visibility_action.setChecked(True)
    else:
        clock.hide()
        toggle_visibility_action.setChecked(False)
    is_clock_displayed = not is_clock_displayed

def toggle_temperature_warning():
    clock.is_warning_enabled = not clock.is_warning_enabled
    toggle_temperature_warning_action.setCheckable(True) if clock.is_warning_enabled else toggle_temperature_warning_action.setCheckable(False)

def handle_tray_icon_click(reason):
    if reason == QSystemTrayIcon.DoubleClick:
        toggle_visibility()

def change_temp_unit(unit):
    clock.temp_unit = unit
    unit_to_action = {
        'C': celsius_action,
        'F': fahrenheit_action,
        'K': kelvin_action
    }
    for action in temp_unit_menu.actions():
        if action == unit_to_action[unit]:
            action.setChecked(True)
        else:
            action.setChecked(False)

def change_font(font):
    clock.text_font = font
    font_to_action = {
        'Courier New': courier_action,
        'Menlo': menlo_action,
        'Consolas': consolas_action
    }
    for action in font_menu.actions():
        if action == font_to_action[font]:
            action.setChecked(True)
        else:
            action.setChecked(False)

def load_settings():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if 'SETTINGS' in config:
        clock.resize(int(config['SETTINGS'].get('width', clock.window_width)), int(config['SETTINGS'].get('height', clock.window_height)))
        x_pos = int(config['SETTINGS'].get('x_pos', 0))
        y_pos = int(config['SETTINGS'].get('y_pos', 0))
        clock.move(x_pos, y_pos)
        change_font(config['SETTINGS'].get('font', clock.text_font))
        change_temp_unit(config['SETTINGS'].get('temp_unit', clock.temp_unit)) 

if __name__ == '__main__':
    is_clock_displayed = True
    app = QApplication(sys.argv)

    # Custom icon - binary
    icon_data = b'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"\n "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n<svg version="1.0" xmlns="http://www.w3.org/2000/svg"\n width="256.000000pt" height="256.000000pt" viewBox="0 0 256.000000 256.000000"\n preserveAspectRatio="xMidYMid meet">\n\n<g transform="translate(0.000000,256.000000) scale(0.100000,-0.100000)"\nfill="#000000" stroke="none">\n<path d="M830 2544 c-189 -50 -337 -195 -385 -379 -13 -50 -15 -148 -15 -609\nl0 -550 -39 -81 c-125 -255 -80 -536 119 -735 76 -75 148 -121 252 -158 64\n-23 88 -26 198 -26 110 0 134 3 198 26 104 37 176 83 252 158 199 199 244 473\n120 730 l-40 81 0 553 c0 608 0 612 -63 730 -109 206 -371 320 -597 260z m277\n-235 c67 -32 109 -75 145 -149 23 -45 23 -45 26 -630 l2 -585 45 -90 c56 -110\n72 -189 56 -277 -33 -188 -171 -326 -359 -359 -172 -31 -367 73 -443 235 -65\n139 -61 249 16 401 l45 90 0 566 c0 632 -1 623 69 714 90 119 254 153 398 84z"/>\n<path d="M899 1475 c-45 -24 -49 -57 -49 -365 l0 -287 -30 -26 c-51 -45 -73\n-101 -68 -172 4 -73 31 -120 92 -163 35 -24 49 -27 116 -27 65 0 82 4 113 25\n118 80 131 244 27 337 l-30 26 0 290 c0 314 -4 342 -56 366 -34 15 -83 13\n-115 -4z"/>\n<path d="M1765 2336 c-75 -33 -74 -155 2 -191 29 -14 65 -16 224 -13 l191 3\n29 33 c40 45 40 99 0 144 l-29 33 -194 3 c-145 1 -200 -1 -223 -12z"/>\n<path d="M1764 1910 c-34 -13 -54 -50 -54 -98 0 -35 6 -49 29 -73 28 -28 33\n-29 120 -29 105 0 134 10 156 56 22 46 11 97 -27 129 -27 23 -38 25 -116 24\n-48 0 -97 -4 -108 -9z"/>\n<path d="M1739 1461 c-39 -39 -41 -106 -5 -148 l24 -28 198 -3 c137 -2 206 0\n226 9 63 26 77 130 23 176 -25 22 -33 23 -231 23 l-206 0 -29 -29z"/>\n<path d="M1765 1056 c-74 -32 -74 -155 0 -191 46 -21 160 -20 205 3 76 38 74\n155 -4 187 -44 18 -160 19 -201 1z"/>\n</g>\n</svg>\n'
    
    # Convert the icon_data bytes to a QByteArray
    icon_data = QByteArray(icon_data)

    # Load the QPixmap from the QByteArray
    pixmap = QPixmap()
    pixmap.loadFromData(icon_data)

    icon = QIcon(pixmap)

    # Create the system tray icon
    tray_icon = QSystemTrayIcon(icon)
    tray_icon.setToolTip('GPU Temperature Monitor')
    exit_action = QAction('Exit', qApp)
    exit_action.triggered.connect(lambda: clock.closeEvent())
    tray_menu = QMenu()

    # Add option to toggle visibility of temperature
    toggle_visibility_action = QAction('Show temperature', qApp, checkable=True, checked=True)
    toggle_visibility_action.triggered.connect(toggle_visibility)
    tray_menu.addAction(toggle_visibility_action)

    # Add option to toggle move and resize
    toggle_move_resize_action = QAction('Toggle Move/Resize', qApp, checkable=True, checked=False)
    toggle_move_resize_action.triggered.connect(toggle_move_resize)
    tray_menu.addAction(toggle_move_resize_action)

    # Add option to toggle temperature warning
    toggle_temperature_warning_action = QAction('Toggle temperature warning', qApp, checkable=True, checked=False)
    toggle_temperature_warning_action.triggered.connect(toggle_temperature_warning)
    tray_menu.addAction(toggle_temperature_warning_action)

    # Add options to change font
    font_menu = tray_menu.addMenu('Font')
    courier_action = QAction('Courier', qApp, checkable=True, checked=True)
    menlo_action = QAction('Menlo', qApp, checkable=True)
    consolas_action = QAction('Consolas', qApp, checkable=True)

    # Connect actions to their respective functions
    courier_action.triggered.connect(lambda: change_font('Courier New'))
    menlo_action.triggered.connect(lambda: change_font('Menlo'))
    consolas_action.triggered.connect(lambda: change_font('Consolas'))

    # Add actions to the font menu
    font_menu.addAction(courier_action)
    font_menu.addAction(menlo_action)
    font_menu.addAction(consolas_action)

    # Add options to change temperature units in the tray menu
    temp_unit_menu = tray_menu.addMenu('Temperature Unit')
    celsius_action = QAction('Celsius', qApp, checkable=True, checked=True)
    fahrenheit_action = QAction('Fahrenheit', qApp, checkable=True)
    kelvin_action = QAction('Kelvin', qApp, checkable=True)

    # Connect actions to their respective functions
    celsius_action.triggered.connect(lambda: change_temp_unit('C'))
    fahrenheit_action.triggered.connect(lambda: change_temp_unit('F'))
    kelvin_action.triggered.connect(lambda: change_temp_unit('K'))

    # Add actions to the temperature unit menu
    temp_unit_menu.addAction(celsius_action)
    temp_unit_menu.addAction(fahrenheit_action)
    temp_unit_menu.addAction(kelvin_action)

    # Add the Restore sub-menu
    restore_menu = tray_menu.addMenu('Restore')

    # Add the Restore Size action and connect it to a function
    restore_size_action = QAction('Restore Size', qApp)
    restore_size_action.triggered.connect(restore_size)
    restore_menu.addAction(restore_size_action)

    # Add the Restore Position action and connect it to a function
    restore_position_action = QAction('Restore Position', qApp)
    restore_position_action.triggered.connect(restore_position)
    restore_menu.addAction(restore_position_action)

    # Add an exit action
    tray_menu.addAction(exit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.activated.connect(handle_tray_icon_click)

    clock = TransparentClock()
    load_settings() # Load settings from the configuration file

    # Show the application in the system tray initially
    tray_icon.show()
    clock.show()

    sys.exit(app.exec_())