import serial
from scannerUtils import findAllScannerPorts
from time import sleep

# Make sure this import path matches your project structure
from discoverQSHFormat import discoverQSHVariants

def main():
    print("🔍 Searching for connected scanners...\n")
    detected = findAllScannerPorts()

    if not detected:
        print("❌ No scanners found. Make sure they are connected and powered on.")
        return

    print("🛠️  Scanners detected:")
    for idx, (port, model) in enumerate(detected, 1):
        print(f"  {idx}. {port} — {model}")

    # User selects port
    try:
        selection = int(input("\nSelect a scanner to connect to (enter number): "))
        if not (1 <= selection <= len(detected)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    port, model = detected[selection - 1]

    try:
        print(f"\n🔌 Connecting to {model} on {port}...")
        ser = serial.Serial(port, 115200, timeout=1)
        sleep(0.2)
        print("✅ Connection established.\n")
    except Exception as e:
        print(f"❌ Failed to open serial port: {e}")
        return

    try:
        # Run the discovery
        results = discoverQSHVariants(ser)

        # Optionally save
        save = input("\nSave results to qsh_results.txt? [y/N]: ").strip().lower()
        if save == "y":
            with open("qsh_results.txt", "w") as f:
                for cmd, resp in results:
                    f.write(f"{cmd} → {resp}\n")
            print("✅ Results saved to qsh_results.txt")

    finally:
        ser.close()
        print("🔒 Serial port closed.")

if __name__ == "__main__":
    main()
