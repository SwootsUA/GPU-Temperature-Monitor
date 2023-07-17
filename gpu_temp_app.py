# gpu_temp_app.py

# GPU Temperature Monitor Application
# Created by Swoots

import sys
import pynvml
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget, QMenu, QAction, qApp, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt, QByteArray
import winsound

displayed_flag = False

class TransparentClock(QWidget):
    def __init__(self):
        super().__init__()
        self.gpu_handle = None
        self.blink_flag = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GPU Temperature')
        self.setGeometry(0, 0, 200, 50)

        # Set window flags to enable transparency and disable window frame
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.temperature_label = QLabel(self)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setStyleSheet("QLabel { font: 24pt 'Courier New', monospace; }")  # Set the font using CSS

        # Initialize NVML to get GPU temperature
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count > 0:
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        # Update the temperature label every second (1000ms)
        timer = QTimer(self)
        timer.timeout.connect(self.update_temperature)
        timer.start(1000)

        self.center_on_screen()

    def center_on_screen(self):
        # Get the center of the screen
        screen_geo = QDesktopWidget().availableGeometry(self)
        self.move((screen_geo.width() - self.width()) - 20, (self.height() - 20))

    def resizeEvent(self, event):
        # Adjust the label size to the window size
        self.temperature_label.setGeometry(self.rect())

    def update_temperature(self):
        if self.gpu_handle:
            temperature = self.get_gpu_temperature()

            if self.blink_flag:
                degree_symbol = "°"  
            else:
                if temperature > 90:  
                    winsound.Beep(750, 100) # Frequency: 750Hz, Duration: 100ms
                degree_symbol =" "

            # change color based on temperature
            gradient_points = [50, 60, 70, 80, 90, 100]
            gradient_colors = [(0, 255, 0), (255, 255, 0), (255, 165, 0), (255, 69, 0), (128, 0, 0)]

            lower_point = max([point for point in gradient_points if point <= temperature])
            upper_point = min([point for point in gradient_points if point >= temperature])

            if lower_point == upper_point:
                ratio = 0
            else:
                ratio = (temperature - lower_point) / (upper_point - lower_point)

            color = self.interpolate_color(gradient_colors[gradient_points.index(lower_point)], gradient_colors[gradient_points.index(upper_point)], ratio)

            color_string = f'rgb({color[0]}, {color[1]}, {color[2]})'
            self.temperature_label.setStyleSheet(f'QLabel {{ color: {color_string}; font-size: 24px; font: 24pt "Courier New", monospace, bold;}}')
            self.temperature_label.setText(f"GPU: {temperature}{degree_symbol}C")
            self.blink_flag = not self.blink_flag  # Toggle blinking

    def get_gpu_temperature(self):
        temperature = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
        # HotSpot offset (Example value, please refer to your GPU specifications)
        if temperature <= 45:
            hotspot_offset = 15
        elif temperature >= 65:
            hotspot_offset = 20
        else:
            hotspot_offset = round(15 + (temperature - 45) * (20 - 15) / (65 - 45))

        return temperature + hotspot_offset

    def interpolate_color(self, color1, color2, ratio):
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = round(r1 + (r2 - r1) * ratio)
        g = round(g1 + (g2 - g1) * ratio)
        b = round(b1 + (b2 - b1) * ratio)
        return r, g, b

    def closeEvent(self, event):
        # Clean up NVML before closing the application
        pynvml.nvmlShutdown()

def tray_icon_clicked(reason):
    if reason == QSystemTrayIcon.DoubleClick:
        global displayed_flag
        if not displayed_flag: 
            clock.show()
        else:
            clock.hide()
        displayed_flag = not displayed_flag 

if __name__ == '__main__':
    displayed_flag = True
    app = QApplication(sys.argv)

    # Custom icon - binary
    icon_data = b'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"\n "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n<svg version="1.0" xmlns="http://www.w3.org/2000/svg"\n width="256.000000pt" height="256.000000pt" viewBox="0 0 256.000000 256.000000"\n preserveAspectRatio="xMidYMid meet">\n\n<g transform="translate(0.000000,256.000000) scale(0.100000,-0.100000)"\nfill="#000000" stroke="none">\n<path d="M830 2544 c-189 -50 -337 -195 -385 -379 -13 -50 -15 -148 -15 -609\nl0 -550 -39 -81 c-125 -255 -80 -536 119 -735 76 -75 148 -121 252 -158 64\n-23 88 -26 198 -26 110 0 134 3 198 26 104 37 176 83 252 158 199 199 244 473\n120 730 l-40 81 0 553 c0 608 0 612 -63 730 -109 206 -371 320 -597 260z m277\n-235 c67 -32 109 -75 145 -149 23 -45 23 -45 26 -630 l2 -585 45 -90 c56 -110\n72 -189 56 -277 -33 -188 -171 -326 -359 -359 -172 -31 -367 73 -443 235 -65\n139 -61 249 16 401 l45 90 0 566 c0 632 -1 623 69 714 90 119 254 153 398 84z"/>\n<path d="M899 1475 c-45 -24 -49 -57 -49 -365 l0 -287 -30 -26 c-51 -45 -73\n-101 -68 -172 4 -73 31 -120 92 -163 35 -24 49 -27 116 -27 65 0 82 4 113 25\n118 80 131 244 27 337 l-30 26 0 290 c0 314 -4 342 -56 366 -34 15 -83 13\n-115 -4z"/>\n<path d="M1765 2336 c-75 -33 -74 -155 2 -191 29 -14 65 -16 224 -13 l191 3\n29 33 c40 45 40 99 0 144 l-29 33 -194 3 c-145 1 -200 -1 -223 -12z"/>\n<path d="M1764 1910 c-34 -13 -54 -50 -54 -98 0 -35 6 -49 29 -73 28 -28 33\n-29 120 -29 105 0 134 10 156 56 22 46 11 97 -27 129 -27 23 -38 25 -116 24\n-48 0 -97 -4 -108 -9z"/>\n<path d="M1739 1461 c-39 -39 -41 -106 -5 -148 l24 -28 198 -3 c137 -2 206 0\n226 9 63 26 77 130 23 176 -25 22 -33 23 -231 23 l-206 0 -29 -29z"/>\n<path d="M1765 1056 c-74 -32 -74 -155 0 -191 46 -21 160 -20 205 3 76 38 74\n155 -4 187 -44 18 -160 19 -201 1z"/>\n</g>\n</svg>\n'
    
    # Convert the icon_data bytes to a QByteArray
    icon_data = QByteArray(icon_data)

    # Load the QPixmap from the QByteArray
    pixmap = QPixmap()
    pixmap.loadFromData(icon_data)

    icon = QIcon(pixmap)

    # Create the system tray icon and add an exit action
    tray_icon = QSystemTrayIcon(icon)
    tray_icon.setToolTip('GPU Temperature Monitor')
    exit_action = QAction('Exit', qApp)
    exit_action.triggered.connect(app.quit)
    tray_menu = QMenu()
    tray_menu.addAction(exit_action)
    tray_icon.setContextMenu(tray_menu)
    tray_icon.activated.connect(tray_icon_clicked)

    clock = TransparentClock()

    # Show the application in the system tray initially
    tray_icon.show()
    clock.show()

    sys.exit(app.exec_())