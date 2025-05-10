import cv2
import numpy as np
from datetime import datetime

class AROverlay:
    def __init__(self):
        """Initialize AR overlay with enhanced settings."""
        # Fonts
        self.title_font = cv2.FONT_HERSHEY_SIMPLEX
        self.info_font = cv2.FONT_HERSHEY_PLAIN
        
        # Colors (BGR format)
        self.colors = {
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'blue': (255, 165, 0),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'yellow': (0, 255, 255)
        }
        
        # Text settings
        self.title_scale = 0.8
        self.info_scale = 1.0
        self.line_type = 2
        self.padding = 10

    def _get_status_color(self, value, threshold=100):
        """Get color based on status value."""
        if value is None:
            return self.colors['red']
        if isinstance(value, (int, float)):
            return self.colors['green'] if value < threshold else self.colors['yellow']
        return self.colors['blue']

    def draw_overlay(self, frame, diagnostics):
        """Draw enhanced network diagnostics overlay."""
        if not diagnostics:
            return frame

        try:
            # Get device status
            device_id = diagnostics.get('device_id', 'Unknown')
            ip = diagnostics.get('ip', 'Unknown')
            ping_stats = diagnostics.get('ping', {})
            ports = diagnostics.get('ports', {})
            
            # Calculate status color based on ping average
            ping_avg = ping_stats.get('avg') if ping_stats else None
            status_color = self._get_status_color(ping_avg)
            
            # Create simplified info text
            info_text = [
                f"Device: {device_id}",
                f"IP: {ip}",
            ]
            
            # Add ping information
            if ping_stats:
                status = ping_stats.get('status', 'unknown')
                info_text.extend([
                    f"Status: {status.upper()}",
                    f"Ping: {ping_stats.get('avg', 'N/A')}ms",
                    f"Loss: {ping_stats.get('loss', 'N/A')}"
                ])
            else:
                info_text.append("Status: No response")
            
            # Add essential port information
            if ports:
                info_text.append("Ports:")
                for port, port_info in sorted(ports.items()):
                    service = port_info.get('service', 'Unknown')
                    status = port_info.get('status', 'unknown')
                    info_text.append(f"  {service}: {status}")
            
            # Calculate box dimensions
            text_height = 30
            box_height = len(info_text) * text_height + self.padding * 2
            box_width = 300  # Reduced width for simpler display
            
            # Draw semi-transparent background
            overlay_rect = np.zeros((box_height, box_width, 3), dtype=np.uint8)
            overlay_rect[:] = (40, 40, 40)  # Dark gray background
            cv2.addWeighted(overlay_rect, 0.8, frame[0:box_height, 0:box_width], 0.2, 0, 
                          frame[0:box_height, 0:box_width])
            
            # Draw title bar
            title_height = 40
            title_rect = np.zeros((title_height, box_width, 3), dtype=np.uint8)
            title_rect[:] = status_color
            frame[0:title_height, 0:box_width] = title_rect
            
            # Draw title
            cv2.putText(frame, f"Network Status", 
                      (self.padding, 25),
                      self.title_font, self.title_scale, self.colors['white'], 
                      self.line_type)
            
            # Draw information
            for i, text in enumerate(info_text):
                y = title_height + self.padding + (i * text_height)
                cv2.putText(frame, text,
                          (self.padding, y),
                          self.info_font, self.info_scale, self.colors['white'],
                          self.line_type)
            
            return frame
            
        except Exception as e:
            print(f"Error drawing overlay: {str(e)}")
            return frame 