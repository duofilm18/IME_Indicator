from win32_api import OCR_IBEAM, OCR_NORMAL

# ============ General ============
STATE_POLL_INTERVAL = 0.1   # 100ms
TRACK_POLL_INTERVAL = 0.01  # 10ms

# ============ 1. Caret Indicator ============
CARET_ENABLE = True
CARET_COLOR_CN = "#FF7800A0"  # Orange, alpha A0
CARET_COLOR_EN = "#0078FF30"  # Blue, alpha 30
CARET_SIZE = 14
CARET_OFFSET_X = 0
CARET_OFFSET_Y = 0
CARET_SHOW_EN = True

# ============ 2. Mouse Indicator ============
MOUSE_ENABLE = True
MOUSE_COLOR_CN = "#FF7800C8"  # Orange
MOUSE_COLOR_EN = "#0078FF30"  # Blue
MOUSE_SIZE = 14
MOUSE_OFFSET_X = 2
MOUSE_OFFSET_Y = 18
MOUSE_SHOW_EN = True

# Cursor shapes to track (not used - cursor check bypassed)
MOUSE_TARGET_CURSORS = [OCR_IBEAM, OCR_NORMAL]

# ============ 3. MQTT LED ============
MQTT_ENABLE = True
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "claude/led"
MQTT_LED_CN = {"r": 255, "g": 13, "b": 0, "pattern": "solid", "duration": 9999}    # Orange (calibrated)
MQTT_LED_EN = {"r": 100, "g": 180, "b": 255, "pattern": "solid", "duration": 9999}  # Light blue

# ============ 4. tmux bridge ============
# IME state file, read by WSL tmux via /mnt/c/Temp/ime_state
IME_STATE_FILE = r"C:\Temp\ime_state"
MQTT_IME_TOPIC = "ime/state"
