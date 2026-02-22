import time
import json
import ctypes
from win32_api import user32, wintypes
import config
from ime_detector import is_chinese_mode
from caret_detector import CaretDetector
from cursor_detector import CursorDetector
from overlay import IndicatorOverlay

def setup_mqtt():
    if not config.MQTT_ENABLE:
        return None
    try:
        import paho.mqtt.client as mqtt
        client = mqtt.Client()
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
        client.loop_start()
        print(f" - MQTT LED: ON ({config.MQTT_BROKER}:{config.MQTT_PORT})")
        return client
    except Exception as e:
        print(f" - MQTT LED: FAILED ({e})")
        return None

def publish_ime_led(mqtt_client, is_chinese):
    if not mqtt_client:
        return
    payload = config.MQTT_LED_CN if is_chinese else config.MQTT_LED_EN
    try:
        mqtt_client.publish(config.MQTT_TOPIC, json.dumps(payload), retain=True)
    except Exception:
        pass

def main():
    caret_detector = CaretDetector()
    cursor_detector = CursorDetector(config.MOUSE_TARGET_CURSORS)

    caret_overlay = None
    if config.CARET_ENABLE:
        caret_overlay = IndicatorOverlay(
            "Caret", config.CARET_SIZE, config.CARET_COLOR_CN,
            config.CARET_COLOR_EN, config.CARET_OFFSET_X, config.CARET_OFFSET_Y
        )

    mouse_overlay = None
    if config.MOUSE_ENABLE:
        mouse_overlay = IndicatorOverlay(
            "Mouse", config.MOUSE_SIZE, config.MOUSE_COLOR_CN,
            config.MOUSE_COLOR_EN, config.MOUSE_OFFSET_X, config.MOUSE_OFFSET_Y
        )

    print("IME Indicator started.")
    if config.CARET_ENABLE: print(f" - Caret indicator: ON (size:{config.CARET_SIZE})")
    if config.MOUSE_ENABLE: print(f" - Mouse indicator: ON (size:{config.MOUSE_SIZE})")

    mqtt_client = setup_mqtt()

    print("Press Ctrl+C to stop.")

    last_state_check_time = 0
    chinese_mode = False
    last_mqtt_state = None
    prev_chinese_mode = None

    caret_active = False
    mouse_active = False

    try:
        while True:
            current_time = time.time()

            # --- A. State detection (100ms) ---
            if current_time - last_state_check_time >= config.STATE_POLL_INTERVAL:
                chinese_mode = is_chinese_mode()

                # MQTT LED (only on state change)
                if chinese_mode != last_mqtt_state:
                    last_mqtt_state = chinese_mode
                    publish_ime_led(mqtt_client, chinese_mode)

                # Write IME state file (for tmux bridge)
                if chinese_mode != prev_chinese_mode:
                    with open(config.IME_STATE_FILE, 'w') as f:
                        f.write('zh' if chinese_mode else 'en')
                    prev_chinese_mode = chinese_mode
                    # MQTT publish for tmux (instant)
                    if mqtt_client:
                        try:
                            mqtt_client.publish(config.MQTT_IME_TOPIC, 'zh' if chinese_mode else 'en', retain=True)
                        except Exception:
                            pass

                # Caret
                if config.CARET_ENABLE:
                    caret_pos_data = caret_detector.get_caret_pos()
                    should_caret = caret_pos_data is not None and (chinese_mode or config.CARET_SHOW_EN)
                    if should_caret != caret_active:
                        caret_active = should_caret
                        if caret_active: caret_overlay.show()
                        else: caret_overlay.hide()

                # Mouse (bypass cursor shape check - Windows Terminal uses custom cursors)
                if config.MOUSE_ENABLE:
                    should_mouse = (chinese_mode or config.MOUSE_SHOW_EN)
                    if should_mouse != mouse_active:
                        mouse_active = should_mouse
                        if mouse_active: mouse_overlay.show()
                        else: mouse_overlay.hide()

                last_state_check_time = current_time

            # --- B. Position tracking ---

            # 1. Caret
            if config.CARET_ENABLE and caret_active:
                cp = caret_detector.get_caret_pos()
                if cp:
                    caret_overlay.update(cp[0], cp[1], chinese_mode, cp[2])

            # 2. Mouse
            if config.MOUSE_ENABLE and mouse_active:
                m_pt = wintypes.POINT()
                if user32.GetCursorPos(ctypes.byref(m_pt)):
                    mouse_overlay.update(m_pt.x, m_pt.y, chinese_mode)

            time.sleep(config.TRACK_POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if caret_overlay: caret_overlay.cleanup()
        if mouse_overlay: mouse_overlay.cleanup()
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        user32.SetProcessDPIAware()
    main()
