# ARNet: Augmented Reality Network Troubleshooting Tool

ARNet is an innovative tool that combines Augmented Reality with network diagnostics to help technicians troubleshoot network devices more efficiently. It overlays real-time network information onto physical devices using QR code identification.

## Features

- Real-time device identification using QR codes
- Live network diagnostics overlay
- Support for multiple network protocols (SNMP, SSH)
- Configurable AR visualization
- Automatic device status monitoring
- Frame capture and logging capabilities

## Requirements

- Python 3.8 or higher
- OpenCV
- NumPy
- pyzbar
- pysnmp
- paramiko
- netmiko
- Flask
- Pillow

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ARNet.git
cd ARNet
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application can be configured through the `config.json` file. Key settings include:

- Camera settings (resolution, FPS)
- Scanning intervals
- Network timeouts
- AR overlay appearance
- QR detection parameters

## Usage

1. Start the application:
```bash
python ARNet/main.py
```

2. Controls:
- 'q' - Quit application
- 'h' - Show help
- 'r' - Refresh device scan
- 's' - Save current frame
- 'c' - Clear current device

3. Point the camera at a network device with a QR code to begin scanning.

## QR Code Format

QR codes should contain JSON-formatted device information:
```json
{
    "device_id": "TL-WR940N",
    "ip": "192.168.0.1",
    "model": "TL-WR940N V6",
    "type": "Router"
}
```

## Logging

Logs are stored in `arnet.log` with detailed information about:
- Device detection events
- Network diagnostic results
- Error conditions
- System status

## Project Structure

```
ARNet/
├── ar_overlay/      # AR visualization components
├── network_tools/   # Network communication and diagnostics
├── qr_generation/   # QR code creation functionality
├── qr_detection/    # QR code scanning and recognition
├── data/           # Data storage
└── main.py         # Application entry point
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV team for computer vision capabilities
- ZBar project for QR code detection
- Network protocol library maintainers
