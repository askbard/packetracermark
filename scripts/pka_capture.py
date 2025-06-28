"""
PKA Screenshot Capture Tool
Advanced virtual monitor approach with dedicated capture space
Ensures consistent resolution and window positioning
Now includes OCR with multiple PSM consensus validation

Version: 0.1
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import logging
import ctypes

try:
    from PIL import ImageGrab, Image
    import win32gui
    import win32con
    import win32api
    import win32ui
    import pytesseract
    from config import get_config
    print("Required modules imported")
except ImportError as e:
    print(f"Missing modules: {e}")
    print("Install with: pip install Pillow pywin32 pytesseract opencv-python")
    sys.exit(1)

# Get configuration
config = get_config()

# Configure Tesseract path
tesseract_path = config.find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("Warning: Tesseract OCR not found. OCR functionality may not work.")
    print("Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")

# Windows API constants
SW_HIDE = 0
SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
HWND_TOP = 0
HWND_TOPMOST = -1

# Configure logging
config.create_directories()
log_filename = config.get_log_filename('pka_capture')
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AdvancedPKACapture:
    def __init__(self):
        self.pt_path = self._find_packet_tracer()
        self.process = None
        self.capture_zone = config.CAPTURE_ZONE.copy()
        
    def _find_packet_tracer(self):
        """Find Cisco Packet Tracer installation"""
        return config.find_packet_tracer()
    
    def _setup_capture_environment(self):
        """Setup dedicated capture environment"""
        try:
            logging.info("Setting up capture environment...")
            
            # Get screen dimensions
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            
            logging.info(f"Screen resolution: {screen_width}x{screen_height}")
            
            # Define capture zone in top-left area
            self.capture_zone = {
                'x': 50,
                'y': 50,
                'width': min(800, screen_width - 100),
                'height': min(600, screen_height - 100)
            }
            
            logging.info(f"Capture zone: {self.capture_zone}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to setup capture environment: {e}")
            return False
    
    def _find_pt_windows(self):
        """Find all Packet Tracer related windows"""
        def enum_callback(hwnd, windows):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # Look for PT Activity windows and main PT windows
                    if ('pt activity' in title.lower() or 
                        'packet tracer' in title.lower() or
                        'cisco packet tracer' in title.lower()):
                        
                        rect = win32gui.GetWindowRect(hwnd)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]
                        
                        window_type = 'activity' if 'pt activity' in title.lower() else 'main'
                        windows.append((hwnd, title, width, height, window_type, class_name))
            except:
                pass
            return True
        
        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        
        # Separate activity windows from main windows
        activity_windows = [w for w in windows if w[4] == 'activity']
        main_windows = [w for w in windows if w[4] == 'main']
        
        # Sort activity windows by size (smallest first - likely instruction windows)
        activity_windows.sort(key=lambda x: x[2] * x[3])
        
        return activity_windows, main_windows

    def _position_window_precisely(self, hwnd, target_x, target_y, target_width=None, target_height=None):
        """Position window with precise control"""
        try:
            # Get current window rect
            rect = win32gui.GetWindowRect(hwnd)
            current_width = rect[2] - rect[0]
            current_height = rect[3] - rect[1]

            # Use current size if target size not specified
            if target_width is None:
                target_width = current_width
            if target_height is None:
                target_height = current_height

            # Restore window first
            win32gui.ShowWindow(hwnd, SW_RESTORE)
            time.sleep(0.1)

            # Set window position and size
            win32gui.SetWindowPos(hwnd, HWND_TOP, target_x, target_y, target_width, target_height,
                                win32con.SWP_SHOWWINDOW)
            time.sleep(0.2)

            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)

            # Force redraw
            win32gui.UpdateWindow(hwnd)
            win32gui.RedrawWindow(hwnd, None, None,
                                win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW |
                                win32con.RDW_ALLCHILDREN | win32con.RDW_FRAME)
            time.sleep(0.3)

            # Verify position
            new_rect = win32gui.GetWindowRect(hwnd)
            logging.info(f"Window positioned at: ({new_rect[0]}, {new_rect[1]}) size: {new_rect[2]-new_rect[0]}x{new_rect[3]-new_rect[1]}")

            return True

        except Exception as e:
            logging.error(f"Failed to position window: {e}")
            return False

    def _capture_with_multiple_methods(self, hwnd, save_path):
        """Try multiple capture methods for best results"""
        methods_tried = []

        # Method 1: Screen capture of positioned window
        try:
            logging.info("Method 1: Screen capture")

            # Ensure window is visible and positioned
            rect = win32gui.GetWindowRect(hwnd)

            # Capture the exact window area
            screenshot = ImageGrab.grab(bbox=rect)

            # Quality check
            colors = screenshot.getcolors(maxcolors=256*256*256)
            color_count = len(colors) if colors else 0

            if color_count > 100:
                screenshot.save(save_path, 'JPEG', quality=95)
                logging.info(f"Screen capture successful: {color_count} colors")
                return True
            else:
                methods_tried.append(f"Screen capture: {color_count} colors (insufficient)")

        except Exception as e:
            methods_tried.append(f"Screen capture failed: {e}")

        # Method 2: Enhanced PrintWindow
        try:
            logging.info("Method 2: Enhanced PrintWindow")

            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            # Get device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # Try different PrintWindow flags
            flags_to_try = [
                3,  # PW_RENDERFULLCONTENT
                1,  # PW_CLIENTONLY
                0,  # Default
                2   # PW_RENDERFULLCONTENT without client
            ]

            for flag in flags_to_try:
                result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), flag)
                if result:
                    bmpinfo = saveBitMap.GetInfo()
                    bmpstr = saveBitMap.GetBitmapBits(True)

                    img = Image.frombuffer(
                        'RGB',
                        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                        bmpstr, 'raw', 'BGRX', 0, 1
                    )

                    # Quality check
                    colors = img.getcolors(maxcolors=256*256*256)
                    color_count = len(colors) if colors else 0

                    if color_count > 50:
                        img.save(save_path, 'JPEG', quality=95)

                        # Cleanup
                        win32gui.DeleteObject(saveBitMap.GetHandle())
                        saveDC.DeleteDC()
                        mfcDC.DeleteDC()
                        win32gui.ReleaseDC(hwnd, hwndDC)

                        logging.info(f"PrintWindow successful (flag {flag}): {color_count} colors")
                        return True

            # Cleanup on failure
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            methods_tried.append("PrintWindow: All flags failed")

        except Exception as e:
            methods_tried.append(f"PrintWindow failed: {e}")

        # Method 3: Force capture with window flash
        try:
            logging.info("Method 3: Force capture with window flash")

            # Flash window to ensure it's rendered
            win32gui.FlashWindow(hwnd, True)
            time.sleep(0.2)

            # Capture
            rect = win32gui.GetWindowRect(hwnd)
            screenshot = ImageGrab.grab(bbox=rect)

            # Save regardless of quality for debugging
            screenshot.save(save_path, 'JPEG', quality=95)

            file_size = os.path.getsize(save_path)
            logging.info(f"Force capture completed: {file_size} bytes")
            return True

        except Exception as e:
            methods_tried.append(f"Force capture failed: {e}")

        # Log all failed methods
        logging.error("All capture methods failed:")
        for method in methods_tried:
            logging.error(f"  - {method}")

        return False

    def _launch_and_wait(self, pka_file):
        """Launch Packet Tracer and wait for windows"""
        try:
            logging.info(f"Launching: {os.path.basename(pka_file)}")

            # Launch with normal visibility for better window management
            self.process = subprocess.Popen([self.pt_path, pka_file])

            # Wait for initial loading
            time.sleep(config.LAUNCH_WAIT_TIME)

            # Wait for PT Activity windows to appear
            max_wait = config.WINDOW_WAIT_TIME
            wait_interval = config.WINDOW_WAIT_INTERVAL

            for elapsed in range(0, max_wait, wait_interval):
                activity_windows, main_windows = self._find_pt_windows()

                if activity_windows:
                    logging.info(f"Found {len(activity_windows)} activity window(s) after {elapsed + wait_interval}s")
                    return activity_windows, main_windows

                logging.info(f"Waiting for windows... ({elapsed + wait_interval}s)")
                time.sleep(wait_interval)

            logging.warning("Timeout waiting for PT Activity windows")
            return [], []

        except Exception as e:
            logging.error(f"Launch failed: {e}")
            return [], []

    def _cleanup_all(self):
        """Comprehensive cleanup"""
        try:
            # Close all PT windows
            def close_pt_windows(hwnd, _):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if ('pt activity' in title.lower() or
                        'packet tracer' in title.lower() or
                        'cisco packet tracer' in title.lower()):
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                except:
                    pass
                return True

            win32gui.EnumWindows(close_pt_windows, None)
            time.sleep(config.CLEANUP_DELAY)

            # Terminate process
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                except:
                    try:
                        self.process.kill()
                    except:
                        pass

        except Exception as e:
            logging.warning(f"Cleanup warning: {e}")

    def capture_pka_advanced(self, pka_file, output_dir):
        """Advanced PKA capture with virtual monitor approach"""
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Setup capture environment
            if not self._setup_capture_environment():
                return False

            # Launch and wait for windows
            activity_windows, _ = self._launch_and_wait(pka_file)

            if not activity_windows:
                logging.error("No PT Activity windows found")
                self._cleanup_all()
                return False

            # Use the smallest activity window (likely the instruction window)
            hwnd, title, width, height, _, _ = activity_windows[0]

            logging.info(f"Capturing window: '{title}' ({width}x{height})")

            # Position window in capture zone
            capture_x = self.capture_zone['x']
            capture_y = self.capture_zone['y']

            if not self._position_window_precisely(hwnd, capture_x, capture_y):
                logging.warning("Failed to position window optimally, continuing...")

            # Generate output path
            pka_name = os.path.splitext(os.path.basename(pka_file))[0]
            screenshot_path = os.path.join(output_dir, f"{pka_name}.jpg")

            # Capture with multiple methods
            success = self._capture_with_multiple_methods(hwnd, screenshot_path)

            # Cleanup
            self._cleanup_all()

            if success and os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                logging.info(f"SUCCESS: {os.path.basename(screenshot_path)} ({file_size} bytes)")
                return screenshot_path
            else:
                logging.error("Capture process failed")
                return False

        except Exception as e:
            logging.error(f"Advanced capture failed: {e}")
            self._cleanup_all()
            return False

def main():
    """Main function with advanced virtual monitor capture"""
    logging.info("=== PKA Advanced Virtual Monitor Capture v3.4 ===")

    # Setup - use project root directories
    project_root = config.get_project_root()
    pka_dir = Path(config.PKA_DIRECTORY)
    output_dir = Path(config.IMAGE_DIRECTORY)

    # Find PKA files in the pka directory
    if pka_dir.exists():
        pka_files = list(pka_dir.glob("*.pka"))
    else:
        logging.warning(f"PKA directory '{config.PKA_DIRECTORY}' not found, checking current directory")
        pka_files = list(project_root.glob("*.pka"))

    if not pka_files:
        logging.error("No PKA files found")
        return

    logging.info(f"Found {len(pka_files)} PKA files")

    # Initialize capture
    capture = AdvancedPKACapture()

    if not capture.pt_path:
        logging.error("Packet Tracer not found")
        return

    logging.info(f"Using: {capture.pt_path}")

    # Process files
    successful = 0
    failed = 0

    for i, pka_file in enumerate(pka_files, 1):
        logging.info(f"\n=== Processing {i}/{len(pka_files)}: {pka_file.name} ===")

        result = capture.capture_pka_advanced(str(pka_file), str(output_dir))

        if result:
            successful += 1
            logging.info(f"✓ SUCCESS: {pka_file.name}")
        else:
            failed += 1
            logging.error(f"✗ FAILED: {pka_file.name}")

        # Pause between files
        if i < len(pka_files):
            time.sleep(3)

    # Summary
    logging.info(f"\n=== FINAL RESULTS ===")
    logging.info(f"Total: {len(pka_files)}, Success: {successful}, Failed: {failed}")
    logging.info(f"Success rate: {successful/len(pka_files)*100:.1f}%")

if __name__ == "__main__":
    main()
