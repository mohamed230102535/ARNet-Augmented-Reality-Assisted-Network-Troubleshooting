import cv2
import sys
import os
import time
import numpy as np

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ar_overlay.overlay import AROverlay
from qr_detection.qr_scanner import QRScanner
from network_tools.device_resolver import DeviceResolver

def print_help():
    """Print help information."""
    print("\nARNet Controls:")
    print("  'q' - Quit application")
    print("  'h' - Show this help")
    print("  'r' - Refresh device scan")
    print("  's' - Save current frame")
    print("  'c' - Clear current device")

def save_frame(frame, device_id):
    """Save the current frame with timestamp."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"frame_{device_id}_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"\nFrame saved as: {filename}")

def list_cameras():
    """List all available cameras."""
    print("\nSearching for available cameras...")
    available_cameras = []
    
    # Try different backends
    backends = [
        (cv2.CAP_ANY, "Auto-detect"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_OPENCV_MJPEG, "OpenCV MJPEG")
    ]
    
    for backend, backend_name in backends:
        print(f"\nTrying {backend_name} backend:")
        for index in range(10):
            try:
                cap = cv2.VideoCapture(index + backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"  Found camera {index}")
                        available_cameras.append((index, backend, backend_name))
                    cap.release()
            except:
                continue
    
    return available_cameras

def process_frame(frame, qr_scanner, last_scan_time, scan_interval=2.0):
    """
    Process a single frame for QR code detection.
    
    Args:
        frame: Input frame from camera
        qr_scanner: QR scanner instance
        last_scan_time: Time of last successful scan
        scan_interval: Minimum time between scans in seconds
    
    Returns:
        tuple: (processed_frame, last_scan_time, device_info)
    """
    current_time = time.time()
    
    # Skip processing if not enough time has passed since last scan
    if current_time - last_scan_time < scan_interval:
        return frame, last_scan_time, None
    
    # Resize frame for faster processing (reduce to 50% of original size)
    height, width = frame.shape[:2]
    small_frame = cv2.resize(frame, (width//2, height//2))
    
    # Convert to grayscale for faster processing
    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
    
    # Try to detect QR code
    try:
        device_info = qr_scanner.scan(gray)
        if device_info:
            return frame, current_time, device_info
    except Exception as e:
        print(f"Error processing frame: {e}")
    
    return frame, last_scan_time, None

def main():
    """Main function to run the ARNet application."""
    print("Initializing ARNet...")
    
    # Initialize camera with optimized settings
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        print("Error: Could not open camera!")
        return
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    
    qr_scanner = QRScanner()
    device_resolver = DeviceResolver()
    ar_overlay = AROverlay()
    
    current_device = None
    current_diagnostics = None
    last_scan_time = 0
    last_ping_time = 0
    scan_interval = 2.0  # seconds between QR scans
    ping_interval = 3.0  # seconds between pings
    frame_count = 0
    skip_frames = 2
    
    print("Starting camera feed...")
    print("\nControls:")
    print("q - Quit application")
    print("h - Show help")
    print("r - Refresh device scan")
    print("s - Save current frame")
    print("c - Clear current device")
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame!")
            break
        frame_count += 1
        if frame_count % (skip_frames + 1) != 0:
            cv2.imshow("ARNet", frame)
            continue
        # QR scan
        current_time = time.time()
        device_info = None
        if current_time - last_scan_time >= scan_interval:
            device_info = qr_scanner.scan(frame)
            last_scan_time = current_time
            if device_info:
                device_id = device_info.get('device_id')
                if device_id != current_device:
                    print(f"\nNew device detected: {device_id}")
                    current_device = device_id
                    # Immediately ping and get diagnostics
                    current_diagnostics = device_resolver.get_device_info(device_info)
                    if current_diagnostics:
                        print("Device info retrieved:")
                        print(f"  Type: {current_diagnostics.get('type', 'unknown')}")
                        print(f"  Location: {current_diagnostics.get('location', 'unknown')}")
                        ping_stats = current_diagnostics.get('ping', {})
                        if ping_stats:
                            print(f"  Ping: {ping_stats.get('avg')}ms (min: {ping_stats.get('min')}ms, max: {ping_stats.get('max')}ms)")
                            print(f"  Packet Loss: {ping_stats.get('loss')}")
                    last_ping_time = current_time
        # Periodically re-ping the device while in view
        if current_device and (time.time() - last_ping_time >= ping_interval):
            if current_diagnostics:
                # Only update ping stats
                ip = current_diagnostics.get('ip')
                if ip:
                    ping_stats = device_resolver.ping(ip)
                    current_diagnostics['ping'] = ping_stats
                    print(f"[Re-ping] {current_device} ({ip}): {ping_stats}")
                    last_ping_time = time.time()
        # Draw overlay if we have diagnostics
        display_frame = frame.copy()
        if current_diagnostics:
            display_frame = ar_overlay.draw_overlay(display_frame, current_diagnostics)
        cv2.imshow("ARNet", display_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('h'):
            print("\nControls:")
            print("q - Quit application")
            print("h - Show help")
            print("r - Refresh device scan")
            print("s - Save current frame")
            print("c - Clear current device")
        elif key == ord('r'):
            last_scan_time = 0
            current_device = None
            current_diagnostics = None
        elif key == ord('s'):
            if current_device:
                save_frame(display_frame, current_device)
        elif key == ord('c'):
            current_device = None
            current_diagnostics = None
            print("Current device cleared")
    camera.release()
    cv2.destroyAllWindows()
    print("\nApplication closed and cleaned up.")

if __name__ == "__main__":
    main() 