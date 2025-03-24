import serial
import time
import sys
from itertools import product
import re

# -----------------------------
# Serial Communication Utils
# -----------------------------
def send_command(ser, cmd):
    full_cmd = cmd.strip() + "\r"
    try:
        ser.reset_input_buffer()
        ser.write(full_cmd.encode("utf-8"))
        response = read_response(ser)
        return response
    except Exception as e:
        return f"[SEND ERROR] {e}"

def read_response(ser, timeout=1.0):
    response_bytes = bytearray()
    start_time = time.time()
    try:
        while True:
            if ser.in_waiting:
                byte = ser.read(1)
                if byte in b'\r\n':
                    break
                response_bytes.extend(byte)
            elif time.time() - start_time > timeout:
                break
        return response_bytes.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        return f"[READ ERROR] {e}"

# -----------------------------
# QSH Permutation Generator
# -----------------------------
def generate_qsh_test_cases():
    freqs = [
        "462550", "462.550", "462.55", "462550.0", "0462550", "462.5500"
    ]
    preFreqFields = ["", "A", "FREQ", "X"]
    mods = ["NFM", "AUTO"]
    atts = ["0", "1"]
    delays = ["-5", "0", "5"]
    code_search = ["", "0", "1"]
    tones = ["", "67", "123", "250", "231"]

    test_cases = []

    for freq, pre in product(freqs, preFreqFields):
        fullFreq = f"{pre}{freq}" if pre else freq
        for mod, att, dly, code, tone in product(mods, atts, delays, code_search, tones):
            base_fields = [fullFreq, "", mod, att, dly, "", code, "", "", "", tone]
            for n in range(2, len(base_fields) + 1):
                cmd = "QSH," + ",".join(base_fields[:n])
                if not re.match(r"^[A-Z]{3},[\w.,\-]*$", cmd):
                    continue
                test_cases.append(cmd)

    return test_cases

# -----------------------------
# QSH Brute Force Discovery
# -----------------------------
def runFullQSHDiscovery(ser, outputFile="qsh_discovery_results.txt", delay=0.05):
    cases = generate_qsh_test_cases()
    successes = []

    print(f"🚀 Starting full QSH discovery — {len(cases)} permutations\n")

    with open(outputFile, "w") as f:
        for i, cmd in enumerate(cases, 1):
            response = send_command(ser, cmd)

            if "ERR" not in response and "NG" not in response:
                print(f"✅ [{i}] {cmd} → {response}")
                f.write(f"{cmd} → {response}\n")
                successes.append((cmd, response))
            elif i % 100 == 0:
                print(f"... {i} tested")

            time.sleep(delay)

    print(f"\n🎯 Discovery complete. {len(successes)} successful or interesting responses.")
    print(f"📁 Results saved to {outputFile}")
    return successes

# -----------------------------
# Port Selection and Main
# -----------------------------
def select_scanner_port():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    detected = []

    print("🔍 Scanning available serial ports...\n")
    for port in ports:
        try:
            with serial.Serial(port.device, 115200, timeout=1) as ser:
                ser.write(b"MDL\r")
                time.sleep(0.2)
                resp = read_response(ser)
                if "BC125AT" in resp:
                    detected.append((port.device, "BC125AT"))
                elif "BCD325" in resp:
                    detected.append((port.device, "BCD325P2"))
                elif resp:
                    detected.append((port.device, f"Unknown: {resp.strip()}"))
        except Exception:
            pass

    if not detected:
        print("❌ No compatible scanners found.")
        return None

    print("🛠️  Detected devices:")
    for i, (port, model) in enumerate(detected, 1):
        print(f"  {i}. {port} — {model}")

    try:
        selection = int(input("\nSelect a port to connect to: "))
        return detected[selection - 1][0]
    except Exception:
        print("❌ Invalid selection.")
        return None

# -----------------------------
# Run Script
# -----------------------------
if __name__ == "__main__":
    port = select_scanner_port()
    if not port:
        sys.exit(1)

    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            print(f"\n🔌 Connected to {port}. Beginning QSH discovery...\n")
            runFullQSHDiscovery(ser)
    except Exception as e:
        print(f"❌ Failed to open port {port}: {e}")

