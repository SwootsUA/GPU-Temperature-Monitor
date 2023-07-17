# config.py

# Gradient points and corresponding colors
GRADIENT_POINTS = [50, 60, 70, 80, 90, 100]
GRADIENT_COLORS = [(0, 255, 0), (255, 255, 0), (255, 165, 0), (255, 69, 0), (128, 0, 0)]

# Hotspot offset for GPU temperature calculation
HOTSPOT_OFFSET = {
    'low': 15,
    'high': 20,
}

# Update interval for the temperature label (in milliseconds)
TEMPERATURE_UPDATE_INTERVAL = 1000
