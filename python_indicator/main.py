import time
import ctypes
from win32_api import user32, wintypes
import config
from ime_detector import is_chinese_mode
from caret_detector import CaretDetector
from cursor_detector import CursorDetector
from overlay import IndicatorOverlay

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
    print("Press Ctrl+C to stop.")

    last_state_check_time = 0
    chinese_mode = False

    caret_active = False
    mouse_active = False

    try:
        while True:
            current_time = time.time()

            # --- A. State detection (100ms) ---
            if current_time - last_state_check_time >= config.STATE_POLL_INTERVAL:
                chinese_mode = is_chinese_mode()

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

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        user32.SetProcessDPIAware()
    main()
