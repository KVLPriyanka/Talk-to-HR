"""
QR Code Generator for HR Portal Mobile Testing (No Ngrok)
"""
import argparse
import os
import socket
from pathlib import Path
import qrcode


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def resolve_network_url(port=5000, explicit_url=None):
    if explicit_url:
        return explicit_url

    env_url = os.environ.get("NETWORK_URL", "").strip() or os.environ.get("PUBLIC_BASE_URL", "").strip()
    if env_url:
        return env_url if env_url.startswith(("http://", "https://")) else f"http://{env_url}"

    local_ip = get_local_ip()
    return f"http://{local_ip}:{port}"


def create_portal_qr(url=None):
    network_url = resolve_network_url(explicit_url=url)
    print(f"Generating QR Code pointing to: {network_url}")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(network_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    root_filename = "hr_portal_qr.png"
    img.save(root_filename)
    print(f"✓ Success! QR code saved to Root: '{os.path.abspath(root_filename)}'")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_filepath = output_dir / "portal_qr.png"
    img.save(output_filepath)
    print(f"✓ Success! QR code saved to Output folder: '{output_filepath.resolve()}'")

    if "http://127.0.0.1" in network_url or "http://localhost" in network_url:
        print("\n👉 This QR targets a local address. For access from other devices, pass a public URL such as:")
        print("   python generate_qr.py --url https://your-public-url")
    else:
        print("\n👉 Scan the image with any phone to open the portal.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a QR code for the HR portal")
    parser.add_argument("--url", help="Use a specific URL for the QR code")
    parser.add_argument("--port", type=int, default=5000, help="Port to use when falling back to the local network IP")
    args = parser.parse_args()

    create_portal_qr(url=args.url)
