# gpu_temp_app.py

# GPU Temperature Monitor Application
# Created by Swoots

import sys
import pynvml
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget, QMenu, QAction, qApp, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
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

    # Load the custom icon from resources
    icon = QIcon('temperature.ico')
    if icon.isNull():
        icon = QIcon.fromTheme('computer')  # Fallback to the default system icon if the custom icon is not found

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