#!/usr/bin/env bash
set -e

sudo modprobe usbserial vendor=0x1965 product=0x0017
sudo usermod -aG plugdev "$USER"

echo "Log out and back in for group changes to take effect."
echo "Then run: python tools/scanner_diagnostics.py --scan"
