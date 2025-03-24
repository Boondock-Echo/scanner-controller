# scannerGUI.py — Hybrid GUI for Scanner Control

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time

from scannerUtils import findAllScannerPorts
from commandLibrary import (
    getScannerInterface,
    readVolume, writeVolume,
    readSquelch, writeSquelch,
    readFrequency, writeFrequency,
    readRSSI, readSMeter,
    readModel, readSWVer
)

class ScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scanner Control")
        self.ser = None
        self.scanner_model = None
        self.scanner_interface = None

        self.port_combo = ttk.Combobox(self.root, state="readonly", width=40)
        self.connect_button = ttk.Button(self.root, text="Connect", command=self.connect_to_scanner)
        # Moved to build_connection_ui

        self.volume_slider = None
        self.squelch_slider = None
        self.command_entry = None
        self.response_text = None

        self.build_connection_ui()

    def build_connection_ui(self):
        self.status_label = ttk.Label(self.root, text="No scanner connected.")
        ttk.Label(self.root, text="Select Scanner Port:").pack(pady=5)
        detected = findAllScannerPorts()
        ports = [f"{port} — {model}" for port, model in detected]
        self.ports_map = {f"{port} — {model}": (port, model) for port, model in detected}

        self.port_combo["values"] = ports or ["No scanners found"]
        if ports:
            self.port_combo.current(0)
        else:
            self.port_combo.config(state="disabled")
        self.port_combo.pack(pady=5)
        self.connect_button.pack(pady=5)
        # Will be re-created in build_connection_ui

    def connect_to_scanner(self):
        selection = self.port_combo.get()
        if selection not in self.ports_map:
            return

        port, model = self.ports_map[selection]
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.scanner_model = model
            self.scanner_interface = getScannerInterface(model)
            self.status_label.config(text=f"Connected to {model} on {port}")
            self.build_control_ui()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def build_control_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Will be re-created in build_connection_ui

        # Volume
        ttk.Label(self.root, text="Volume").pack()
        self.volume_slider = ttk.Scale(self.root, from_=0, to=1, orient=tk.HORIZONTAL, command=self.on_volume_change)
        self.volume_slider.pack(fill=tk.X, padx=20)
        try:
            vol = readVolume(self.ser, self.scanner_model)
            if isinstance(vol, float):
                self.volume_slider.set(vol)
        except: pass

        # Squelch
        ttk.Label(self.root, text="Squelch").pack()
        self.squelch_slider = ttk.Scale(self.root, from_=0, to=1, orient=tk.HORIZONTAL, command=self.on_squelch_change)
        self.squelch_slider.pack(fill=tk.X, padx=20)
        try:
            squelch = readSquelch(self.ser, self.scanner_model)
            if isinstance(squelch, float):
                self.squelch_slider.set(squelch)
        except: pass

        # Command entry
        ttk.Label(self.root, text="Command Entry (e.g., 'read volume', 'send key 123.'):").pack(pady=(10, 0))
        self.command_entry = ttk.Entry(self.root, width=50)
        self.command_entry.pack(pady=5)
        ttk.Button(self.root, text="Send Command", command=self.on_send_command).pack()

        # Response box
        self.response_text = tk.Text(self.root, height=10, width=60)
        self.response_text.pack(pady=10)

    def on_volume_change(self, val):
        try:
            v = float(val)
            response = writeVolume(self.ser, self.scanner_model, v)
            self.log_response(f"Set volume → {response}")
        except Exception as e:
            self.log_response(f"[Volume Error] {e}")

    def on_squelch_change(self, val):
        try:
            s = float(val)
            response = writeSquelch(self.ser, self.scanner_model, s)
            self.log_response(f"Set squelch → {response}")
        except Exception as e:
            self.log_response(f"[Squelch Error] {e}")

    def on_send_command(self):
        userInput = self.command_entry.get().strip().lower()
        try:
            if userInput == "read volume":
                result = readVolume(self.ser, self.scanner_model)
            elif userInput.startswith("write volume"):
                value = float(userInput.split(" ", 2)[2])
                result = writeVolume(self.ser, self.scanner_model, value)
            elif userInput == "read squelch":
                result = readSquelch(self.ser, self.scanner_model)
            elif userInput.startswith("write squelch"):
                value = float(userInput.split(" ", 2)[2])
                result = writeSquelch(self.ser, self.scanner_model, value)
            elif userInput == "read frequency":
                result = readFrequency(self.ser, self.scanner_model)
            elif userInput.startswith("write frequency"):
                value = float(userInput.split(" ", 2)[2])
                result = writeFrequency(self.ser, self.scanner_model, value)
            elif userInput == "read rssi":
                result = readRSSI(self.ser, self.scanner_model)
            elif userInput == "read smeter":
                result = readSMeter(self.ser, self.scanner_model)
            elif userInput == "read model":
                result = readModel(self.ser, self.scanner_model)
            elif userInput == "read version":
                result = readSWVer(self.ser, self.scanner_model)
            elif userInput.startswith("send key"):
                keySeq = userInput.split(" ", 2)[2]
                result = getScannerInterface(self.scanner_model).sendKey(self.ser, keySeq)
            else:
                result = f"Unknown command: {userInput}"
        except Exception as e:
            result = f"[Command Error] {e}"
        self.log_response(f"> {userInput}\n{result}\n")

    def log_response(self, msg):
        self.response_text.insert(tk.END, msg + "\n")
        self.response_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerGUI(root)
    root.mainloop()
