# GPU Temperature Monitor

This is a simple GPU temperature monitor application written in Python using PyQt5 and NVIDIA Management Library (pynvml). The application displays the GPU temperature in a transparent window and changes the label color based on the temperature gradient.

## Requirements

- Python 3.x
- PyQt5 (`pip install PyQt5`)
- NVIDIA Management Library (`pip install pynvml`)
- NVIDIA GPU with installed drivers

## How to Use

1. Make sure you have Python and the required libraries installed.
2. Ensure that you have an NVIDIA GPU with installed drivers.
3. Download the code provided in the `gpu_temp_app.py` file and save it on your computer.

## Custom Configuration

A custom configuration file named `config.py` is provided with the application. This file contains constants and configuration settings that can be adjusted by the user to customize the application's behavior. Before running the application, ensure that the `config.py` file is located in the same directory as `gpu_temp_app.py`.

Feel free to adjust the values in the `config.py` file based on your preferences or GPU specifications.

## Execution

To run the application, execute the following command in your terminal or command prompt:

```python gpu_temp_app.py```

Please ensure that the `gpu_temp_app.py` script and the `config.py` file are located in the same directory. The application will use the constants defined in the `config.py` file for customization and GPU temperature calculations.

## Instructions

1. Upon running the application, a system tray icon will appear.
2. Double-click on the system tray icon to show/hide the GPU temperature monitor window.
3. The temperature label will be updated every second.
4. The label color will change according to the temperature gradient, indicating different temperature ranges.
5. Font can be changed to one of the three font options by right-clicking on the system tray icon and choosing "Font" then pick from the available fonts.
6. You can toggle move and resize actions by selecting "Toggle Move/Resize" in the system tray menu.
7. Size and position can be restored by selecting "Restore Size" and "Restore Position" in the "Restore" menu.
8. To change the temperature unit, right-click on the system tray icon and select "Temperature Unit," then choose Celsius, Fahrenheit, or Kelvin.

## Compiling to EXE

If you want to compile the Python script into an executable (EXE) file, you can use tools like `pyinstaller` or `cx_Freeze`. Below are the steps to compile the script using `pyinstaller`:

1. Install `pyinstaller`:

```pip install pyinstaller```

2. Compile the script into an EXE:

```pyinstaller --onefile --noconsole --clean gpu_temp_app.py```

3. After the compilation is complete, you will find the EXE file in the `dist` directory.

Please note that when you compile the script to an EXE, the resulting executable will read the configuration settings from the `config.py` file during the build process. However, once compiled, the EXE file will remain unchanged and will use the configuration values stored in the `config.py` file that was present at the time of compilation.

If you want to make changes to the application's behavior after compiling it into an EXE, you will need to modify the `config.py` file and then recompile the script to generate a new EXE with the updated settings.

## Note

Please be aware that the `hotspot_offset` variable in the code is set to a default value (15). For accurate temperature readings, you should replace this value with the actual hotspot offset from your GPU specifications.

## License

This application is licensed under the MIT License. Feel free to use, modify, and distribute it according to the terms of the MIT License. For more information about the license, please refer to the `LICENSE` file in this repository.

---

This README provides an overview of the GPU Temperature Monitor application and how to use it, including instructions for compiling the Python script into an executable (EXE) file. If you encounter any issues or have questions, feel free to reach out or refer to the provided code for further details.
