#!/bin/bash

# Script to permanently configure BC125AT to use usbserial instead of cdc_acm
# For user boondock:boondock at /opt/boondock/scanner-controller

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)."
    exit 1
fi

# Define paths and variables
SCRIPT_DIR="/opt/boondock/scanner-controller"
SCRIPT_PATH="$SCRIPT_DIR/bc125at_setup.sh"
SERVICE_PATH="/etc/systemd/system/bc125at-setup.service"
UDEV_RULE="/etc/udev/rules.d/99-bc125at.rules"
BLACKLIST_FILE="/etc/modprobe.d/blacklist-cdc-acm.conf"
VENDOR_ID="0x1965"
PRODUCT_ID="0x0017"

# Step 1: Create the runtime script
cat << 'EOF' > "$SCRIPT_PATH"
#!/bin/bash

# Runtime script to force BC125AT to use usbserial instead of cdc_acm

# Define vendor and product IDs for BC125AT
VENDOR_ID="0x1965"
PRODUCT_ID="0x0017"

echo "Removing cdc_acm module..."
modprobe -r cdc_acm
if [ $? -eq 0 ]; then
    echo "cdc_acm removed successfully."
else
    echo "Failed to remove cdc_acm or it was not loaded."
fi

echo "Loading usbserial with vendor=$VENDOR_ID product=$PRODUCT_ID..."
modprobe usbserial vendor=$VENDOR_ID product=$PRODUCT_ID
if [ $? -eq 0 ]; then
    echo "usbserial loaded successfully."
else
    echo "Failed to load usbserial. Check if module exists or IDs are correct."
    exit 1
fi

echo "Checking for device registration..."
sleep 2  # Give the system a moment to register the device
dmesg | tail -n 10

echo "Listing available ttyUSB devices:"
ls /dev/ttyUSB* 2>/dev/null || echo "No ttyUSB devices found."

echo "Setup complete. Test your device on /dev/ttyUSB0 (or similar)."
EOF

# Make the runtime script executable and set ownership
chmod +x "$SCRIPT_PATH"
chown boondock:boondock "$SCRIPT_PATH"

# Step 2: Create the systemd service
cat << EOF > "$SERVICE_PATH"
[Unit]
Description=Force BC125AT to use usbserial instead of cdc_acm
After=network.target

[Service]
Type=oneshot
ExecStart=$SCRIPT_PATH
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable the systemd service
systemctl daemon-reload
systemctl enable bc125at-setup.service
systemctl start bc125at-setup.service

# Step 3: Blacklist cdc_acm module
if [ ! -f "$BLACKLIST_FILE" ]; then
    echo "Blacklisting cdc_acm module..."
    echo "blacklist cdc_acm" > "$BLACKLIST_FILE"
    update-initramfs -u 2>/dev/null || echo "Skipping initramfs update (may not be needed)."
else
    echo "cdc_acm already blacklisted."
fi

# Step 4: Create udev rule for hot-plugging
cat << EOF > "$UDEV_RULE"
SUBSYSTEM=="usb", ATTR{idVendor}=="$VENDOR_ID", ATTR{idProduct}=="$PRODUCT_ID", RUN+="$SCRIPT_PATH"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

# Step 5: Set ownership of directory and files
chown -R boondock:boondock "$SCRIPT_DIR"

# Step 6: Run the script now to apply changes immediately
echo "Applying changes immediately..."
bash "$SCRIPT_PATH"

# Final instructions
echo "Setup complete!"
echo " - The script is installed at $SCRIPT_PATH"
echo " - Systemd service is enabled and running (bc125at-setup.service)"
echo " - cdc_acm is blacklisted"
echo " - Udev rule is set for hot-plugging at $UDEV_RULE"
echo "Reboot your Pi to verify persistence, then check with 'ls /dev/ttyUSB*'"