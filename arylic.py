#!/usr/bin/env python3
"""
Arylic Up2Stream TCP API client.

Protocol: TCP port 8899
Packet layout:
  [4B header][4B length LE][4B checksum LE][8B reserved][payload]
"""

import socket
import struct
import argparse

HEADER = bytes([0x18, 0x96, 0x18, 0x20])
PORT = 8899
TIMEOUT = 5.0

PLM_CODES = {
    "000": "Idle",
    "001": "AirPlay",
    "002": "DLNA",
    "010": "online playlist",
    "011": "USB playlist",
    "020": "HTTP API",
    "031": "Spotify Connect",
    "032": "TIDAL Connect (A97 only)",
    "040": "LINE-IN",
    "041": "Bluetooth",
    "045": "Coaxial",
    "047": "LINE-IN 2",
    "049": "HDMI",
    "051": "USB DAC",
    "053": "External Bluetooth",
    "054": "Phono",
    "056": "Optical 2",
    "057": "Coaxial 2",
    "058": "ARC",
    "099": "Slave mode"
}


def build_packet(command: str) -> bytes:
    payload = command.encode("ascii")
    length = len(payload)
    checksum = sum(payload) & 0xFFFFFFFF
    header = HEADER
    header += struct.pack("<I", length)
    header += struct.pack("<I", checksum)
    header += b"\x00" * 8
    return header + payload


def parse_packet(data: bytes) -> str:
    """Extract the payload string from a response packet, or return raw if unframed."""
    if len(data) >= 20 and data[:4] == HEADER:
        length = struct.unpack("<I", data[4:8])[0]
        payload = data[20: 20 + length]
        return payload.decode("ascii", errors="replace")
    # Device sometimes responds without packet framing
    return data.decode("ascii", errors="replace").strip()


def send_command(host: str, command: str, port: int = PORT) -> str:
    packet = build_packet(command)
    with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
        sock.sendall(packet)
        response = sock.recv(4096)
    return parse_packet(response)


def decode_plm(response: str) -> str:
    # Expected: AXX+PLM+XXX
    parts = response.strip().split("+")
    if len(parts) >= 3:
        code = parts[-1].strip()
        return PLM_CODES.get(code, f"Unknown ({code})")
    return f"Unexpected response: {response}"

def show_examples():
    print("Example commands:")
    print("  MCU+PLM+GET            - Get current input mode")
    print("  MCU+VOL+GET            - Get current volume")
    print("  MCU+VOL+SET+XX         - Set volume to XX (0-100)")
    print("  MCU+PLM+SET+XXX        - Set input mode to XXX (see PLM_CODES)")
    print("  MCU+SYS+REBOOT         - Reboot the device")
    print("  MCU+SYS+INFO           - Get system information")
    print("  MCU+NET+SCAN           - Scan for Wi-Fi networks")
    print("  MCU+NET+SET+SSID+PW    - Connect to Wi-Fi network with SSID and password")
    print("  MCU+PAS+RAKOIT:CFE:1&  - Enable crossfilter")
    print("  MCU+PAS+RAKOIT:CFE:0&  - Disable crossfilter")
    print("  MCU+PAS+RAKOIT:CFF&    - Get crossfilter frequency point")
    print("  MCU+PAS+RAKOIT:CFF:80& - Set crossfilter frequency point, {cffreq} ranges [50,300]")

def main():
    parser = argparse.ArgumentParser(description="Arylic Up2Stream TCP API client")
    parser.add_argument("host", help="IP address of the Arylic device")
    parser.add_argument("--port", type=int, default=PORT, help=f"TCP port (default {PORT})")
    parser.add_argument("--command", default="MCU+PLM+GET", help="Raw command to send")
    parser.add_argument("--examples", action="store_true", help="Show example commands")
    args = parser.parse_args()
    
    if args.examples:
        show_examples()
        return
    
    print(f"Connecting to {args.host}:{args.port}")
    print(f"Sending: {args.command}")

    response = send_command(args.host, args.command, args.port)
    print(f"Response: {response}")

    if args.command == "MCU+PLM+GET":
        print(f"Input mode: {decode_plm(response)}")


if __name__ == "__main__":
    main()
