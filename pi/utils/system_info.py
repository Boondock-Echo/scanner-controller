import subprocess
import psutil
import glob

def get_system_info():
    try:
        # Get IP address
        ip_output = subprocess.run(['ip', 'addr', 'show', 'wlan0'], capture_output=True, text=True)
        ip_match = ip_output.stdout.split('inet ')[1].split('/')[0] if 'inet ' in ip_output.stdout else 'Not connected'
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_used = round(memory.used / 1024 / 1024, 2)  # Convert to MB
        memory_total = round(memory.total / 1024 / 1024, 2)  # Convert to MB
        
        return {
            'ip_address': ip_match,
            'cpu_usage': round(cpu_usage, 1),
            'memory_used': memory_used,
            'memory_total': memory_total
        }
    except Exception:
        return {
            'ip_address': 'Error',
            'cpu_usage': 'Error',
            'memory_used': 'Error',
            'memory_total': 'Error'
        }

def get_usb_serial_devices():
    try:
        # List USB-to-serial devices (e.g., /dev/ttyUSB*, /dev/ttyACM*)
        devices = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        return [os.path.basename(device) for device in devices]
    except Exception:
        return []