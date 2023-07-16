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

## Execution

To run the application, execute the following command in your terminal or command prompt:

```python gpu_temp_app.py```

## Instructions

1. Upon running the application, a system tray icon will appear.
2. Double-click on the system tray icon to show/hide the GPU temperature monitor window.
3. The temperature label will be updated every second.
4. The label color will change according to the temperature gradient, indicating different temperature ranges.

## Compiling to EXE

If you want to compile the Python script into an executable (EXE) file, you can use tools like `pyinstaller` or `cx_Freeze`. Below are the steps to compile the script using `pyinstaller`:

1. Install `pyinstaller`:

```pip install pyinstaller```

2. Compile the script into an EXE:

```pyinstaller --onefile gpu_temp_app.py```


3. After the compilation is complete, you will find the EXE file in the `dist` directory.

## Note

Please be aware that the `hotspot_offset` variable in the code is set to a default value (15). For accurate temperature readings, you should replace this value with the actual hotspot offset from your GPU specifications.

## License

This application is licensed under the MIT License. Feel free to use, modify, and distribute it according to the terms of the MIT License. For more information about the license, please refer to the `LICENSE` file in this repository.

---

This README provides an overview of the GPU Temperature Monitor application and how to use it, including instructions for compiling the Python script into an executable (EXE) file. If you encounter any issues or have questions, feel free to reach out or refer to the provided code for further details. Happy monitoring!

---

<p align="center">
    <a href="https://github.com/SwootsUA/GPU-Temperature-Monitor">View on GitHub</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/SwootsUA/GPU-Temperature-Monitor/issues">Report Bug</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/SwootsUA/GPU-Temperature-Monitor/pulls">Request Feature</a>
</p>
