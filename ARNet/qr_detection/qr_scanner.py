import cv2
from pyzbar.pyzbar import decode
import json

class QRScanner:
    def __init__(self):
        """Initialize QR scanner with default settings."""
        self.last_scan = None

    def scan(self, frame):
        """
        Scan frame for QR codes and return device information if found.
        
        Args:
            frame: OpenCV image frame
            
        Returns:
            dict: Device information from QR code or None if no QR found
        """
        try:
            # Decode QR codes in the frame
            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                # Convert QR data to string
                data = obj.data.decode('utf-8')
                
                try:
                    # Parse JSON data from QR code
                    device_info = json.loads(data)
                    self.last_scan = device_info
                    return device_info
                except json.JSONDecodeError:
                    print(f"Invalid QR code data format: {data}")
                    continue
                    
            return None
            
        except Exception as e:
            print(f"Error scanning QR code: {str(e)}")
            return None

    def get_last_scan(self):
        """Return the last successfully scanned device information."""
        return self.last_scan 