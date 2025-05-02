import qrcode
import json
import os

def generate_qr_code(device_id, ip, output_dir="../data/qr_samples"):
    """
    Generate a QR code for a network device.
    
    Args:
        device_id: Device identifier (e.g., 'SW1')
        ip: Device IP address
        output_dir: Directory to save QR code images
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create device info dictionary
    device_info = {
        "device_id": device_id,
        "ip": ip
    }
    
    # Convert to JSON string
    json_data = json.dumps(device_info)
    
    # Create QR object with simpler settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    
    # Add data and make QR code
    qr.add_data(json_data)
    qr.make(fit=True)
    
    # Create image with black and white colors
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code
    output_path = os.path.join(output_dir, f"{device_id}_qr.png")
    qr_image.save(output_path)
    print(f"QR code saved to: {output_path}")
    
    # Print the data that was encoded (for verification)
    print(f"Encoded data: {json_data}")

def main():
    """Generate QR codes for test devices."""
    # Test devices with their IDs and IPs
    test_devices = [
        ("SW1", "192.168.1.10"),
        ("RT1", "192.168.1.1"),
        ("AP1", "192.168.1.20")
    ]
    
    print("Generating QR codes for test devices...")
    for device_id, ip in test_devices:
        print(f"\nGenerating QR code for {device_id}...")
        generate_qr_code(device_id, ip)
    
    print("\nAll QR codes have been generated!")
    print("You can find them in the 'data/qr_samples' directory.")

if __name__ == "__main__":
    main() 