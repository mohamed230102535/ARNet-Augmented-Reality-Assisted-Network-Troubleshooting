import subprocess
import platform
import json
import os
import socket
import time
from datetime import datetime

class DeviceResolver:
    def __init__(self):
        """Initialize device resolver with enhanced settings."""
        self.device_map = self._load_device_map()
        self.common_ports = {
            22: 'SSH',
            80: 'HTTP',
            443: 'HTTPS',
            23: 'Telnet',
            21: 'FTP'
        }

    def _load_device_map(self):
        """Load device mapping from JSON file."""
        try:
            map_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'device_map.json')
            if os.path.exists(map_path):
                with open(map_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading device map: {str(e)}")
            return {}

    def ping(self, ip, count=2):
        """
        Enhanced ping function with multiple attempts and statistics.
        
        Args:
            ip: IP address to ping
            count: Number of ping attempts
            
        Returns:
            dict: Ping statistics
        """
        try:
            # Windows ping command with shorter timeout
            if platform.system().lower() == "windows":
                ping_cmd = ["ping", "-n", str(count), "-w", "1000", ip]  # 1 second timeout
            else:
                ping_cmd = ["ping", "-c", str(count), "-W", "1", ip]  # 1 second timeout

            result = subprocess.run(ping_cmd, 
                                 capture_output=True, 
                                 text=True,
                                 timeout=2)  # Overall timeout of 2 seconds
            
            # Parse ping statistics
            output = result.stdout
            times = []
            packet_loss = "100%"
            
            if "time=" in output:
                # Extract ping times
                for line in output.split('\n'):
                    if "time=" in line:
                        try:
                            time_str = line.split("time=")[1].split("ms")[0].strip()
                            times.append(float(time_str))
                        except:
                            continue
                
                # Calculate statistics
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    packet_loss = f"{(1 - len(times)/count) * 100}%"
                    
                    return {
                        'avg': round(avg_time, 2),
                        'min': round(min_time, 2),
                        'max': round(max_time, 2),
                        'loss': packet_loss,
                        'status': 'up'
                    }
            
            return {
                'avg': None,
                'min': None,
                'max': None,
                'loss': packet_loss,
                'status': 'down'
            }
            
        except subprocess.TimeoutExpired:
            print(f"Ping timeout for {ip}")
            return {
                'avg': None,
                'min': None,
                'max': None,
                'loss': '100%',
                'status': 'down'
            }
        except Exception as e:
            print(f"Error pinging device: {str(e)}")
            return None

    def check_port(self, ip, port, timeout=0.5):
        """Check if a port is open using socket connection."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def get_device_info(self, device_info):
        """
        Get comprehensive device information including enhanced diagnostics.
        
        Args:
            device_info: Dictionary containing device_id and ip
            
        Returns:
            dict: Complete device diagnostics
        """
        try:
            device_id = device_info.get('device_id')
            ip = device_info.get('ip')
            
            if not device_id or not ip:
                print(f"Missing device_id or ip in device_info: {device_info}")
                return None

            # Get device details from map
            device_details = self.device_map.get(device_id, {})
            if not device_details:
                print(f"Device {device_id} not found in device map")
                return None
            
            # Get ping statistics
            ping_stats = self.ping(ip)
            if not ping_stats:
                print(f"Failed to get ping statistics for {ip}")
                ping_stats = {
                    'avg': None,
                    'min': None,
                    'max': None,
                    'loss': '100%',
                    'status': 'down'
                }
            
            # Only check essential ports for faster response
            essential_ports = {
                80: 'HTTP',
                443: 'HTTPS'
            }
            
            # Check essential ports
            ports = {}
            for port, service in essential_ports.items():
                is_open = self.check_port(ip, port)
                ports[port] = {
                    'service': service,
                    'status': 'open' if is_open else 'closed'
                }
            
            # Add device-specific ports if available
            device_ports = device_details.get('ports', {})
            for port, service in device_ports.items():
                try:
                    port_num = int(port)
                    is_open = self.check_port(ip, port_num)
                    ports[port_num] = {
                        'service': service,
                        'status': 'open' if is_open else 'closed'
                    }
                except ValueError:
                    print(f"Invalid port number in device map: {port}")
            
            # Build enhanced diagnostics
            diagnostics = {
                'device_id': device_id,
                'ip': ip,
                'type': device_details.get('type', 'unknown'),
                'location': device_details.get('location', 'unknown'),
                'model': device_details.get('model', 'unknown'),
                'ping': ping_stats,
                'ports': ports,
                'last_check': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return diagnostics
            
        except Exception as e:
            print(f"Error getting device info: {str(e)}")
            return None 