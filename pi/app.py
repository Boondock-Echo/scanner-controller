from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os
from utils.system_info import get_system_info, get_usb_serial_devices

app = Flask(__name__)

# File to store MQTT settings
MQTT_CONFIG_FILE = '/home/pi/mqtt_config.json'

def load_mqtt_config():
    try:
        if os.path.exists(MQTT_CONFIG_FILE):
            with open(MQTT_CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def scan_wifi_networks():
    try:
        result = subprocess.run(['sudo', 'iwlist', 'wlan0', 'scan'], capture_output=True, text=True, check=True)
        networks = []
        seen_ssids = set()
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'ESSID:' in line:
                ssid = line.split('ESSID:"')[1].split('"')[0]
                if ssid and ssid not in seen_ssids:
                    networks.append({'ssid': ssid})
                    seen_ssids.add(ssid)
        return networks
    except Exception:
        return []

def subnet_mask_to_cidr(mask):
    try:
        return sum([bin(int(x)).count('1') for x in mask.split('.')])
    except Exception:
        return 24

@app.route('/')
def index():
    system_info = get_system_info()
    usb_serial_devices = get_usb_serial_devices()
    return render_template('index.html', system_info=system_info, usb_serial_devices=usb_serial_devices)

@app.route('/wifi')
def wifi():
    mqtt_config = load_mqtt_config()
    return render_template('wifi.html', mqtt_config=mqtt_config)

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/wifi/networks', methods=['GET'])
def get_wifi_networks():
    networks = scan_wifi_networks()
    return jsonify(networks)

@app.route('/wifi', methods=['POST'])
def configure_wifi():
    data = request.get_json()
    ssid = data.get('ssid')
    password = data.get('password')
    static_ip = data.get('staticIp')
    subnet_mask = data.get('subnetMask')
    gateway = data.get('gateway')
    dns = data.get('dns')

    if not ssid:
        return jsonify({'message': 'SSID is required'}), 400

    try:
        wifi_config = f"""
network={{
    ssid="{ssid}"
    psk="{password}" if password else 'key_mgmt=NONE'
}}
"""
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
            f.write(wifi_config)

        dhcpcd_config = ""
        if static_ip and subnet_mask:
            dhcpcd_config += f"""
interface wlan0
static ip_address={static_ip}/{subnet_mask_to_cidr(subnet_mask)}
"""
            if gateway:
                dhcpcd_config += f"static routers={gateway}\n"
            if dns:
                dhcpcd_config += f"static domain_name_servers={dns}\n"

        if dhcpcd_config:
            with open('/etc/dhcpcd.conf', 'a') as f:
                f.write(dhcpcd_config)

        subprocess.run(['wpa_cli', '-i', 'wlan0', 'reconfigure'], check=True)
        if dhcpcd_config:
            subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'], check=True)

        return jsonify({'message': 'WiFi configured successfully'})
    except Exception as e:
        return jsonify({'message': f'Error configuring WiFi: {str(e)}'}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        subprocess.run(['sudo', 'poweroff'], check=True)
        return jsonify({'message': 'Shutting down...'})
    except Exception as e:
        return jsonify({'message': f'Error shutting down: {str(e)}'}), 500

@app.route('/reboot', methods=['POST'])
def reboot():
    try:
        subprocess.run(['sudo', 'reboot'], check=True)
        return jsonify({'message': 'Rebooting...'})
    except Exception as e:
        return jsonify({'message': f'Error rebooting: {str(e)}'}), 500

@app.route('/mqtt', methods=['POST'])
def configure_mqtt():
    data = request.get_json()
    config = {
        'host': data.get('host', ''),
        'port': int(data.get('port', 1883)),
        'username': data.get('username', ''),
        'password': data.get('password', '')
    }

    try:
        with open(MQTT_CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return jsonify({'message': 'MQTT settings saved successfully'})
    except Exception as e:
        return jsonify({'message': f'Error saving MQTT settings: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)