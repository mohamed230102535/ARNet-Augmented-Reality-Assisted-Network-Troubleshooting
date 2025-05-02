import cv2
import sys
import os
import time

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
    """Save the current frame with overlay."""
    try:
        # Create screenshots directory if it doesn't exist
        os.makedirs('screenshots', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/arnet_{device_id}_{timestamp}.png"
        
        # Save frame
        cv2.imwrite(filename, frame)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Error saving screenshot: {str(e)}")

def main():
    """
    Main entry point for the ARNet application.
    Initializes camera feed, QR scanner, and AR overlay.
    """
    try:
        print("\nInitializing ARNet application...")
        print("Initializing components...")
        
        # Initialize components
        qr_scanner = QRScanner()
        device_resolver = DeviceResolver()
        ar_overlay = AROverlay()
        
        print("Starting camera feed...")
        # Start camera feed
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera!")
            return
            
        print("Camera started successfully!")
        print_help()
        
        # Application state
        current_device = None
        current_diagnostics = None
        last_scan_time = 0
        scan_interval = 5  # seconds
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Process frame
            current_time = time.time()
            
            # Scan for QR codes periodically
            if current_time - last_scan_time >= scan_interval:
                device_info = qr_scanner.scan(frame)
                
                if device_info:
                    device_id = device_info.get('device_id')
                    if device_id != current_device:
                        print(f"\nNew device detected: {device_id}")
                        current_device = device_id
                        # Get network diagnostics
                        current_diagnostics = device_resolver.get_device_info(device_info)
                        if current_diagnostics:
                            print("Device info retrieved:")
                            print(f"  Type: {current_diagnostics.get('type', 'unknown')}")
                            print(f"  Location: {current_diagnostics.get('location', 'unknown')}")
                            ping_stats = current_diagnostics.get('ping', {})
                            if ping_stats:
                                print(f"  Ping: {ping_stats.get('avg')}ms (min: {ping_stats.get('min')}ms, max: {ping_stats.get('max')}ms)")
                                print(f"  Packet Loss: {ping_stats.get('loss')}")
                
                last_scan_time = current_time

            # Draw overlay if we have diagnostics
            if current_diagnostics:
                frame = ar_overlay.draw_overlay(frame, current_diagnostics)

            # Display the frame
            cv2.imshow('ARNet - Network Troubleshooting', frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\nQuitting application...")
                break
            elif key == ord('h'):
                print_help()
            elif key == ord('r'):
                print("\nForcing device rescan...")
                last_scan_time = 0
                current_device = None
                current_diagnostics = None
            elif key == ord('s'):
                if current_device:
                    save_frame(frame, current_device)
            elif key == ord('c'):
                print("\nClearing current device...")
                current_device = None
                current_diagnostics = None

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        print("Application closed.")

if __name__ == "__main__":
    main() 