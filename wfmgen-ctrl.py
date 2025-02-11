#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import serial
import serial.tools.list_ports

class WaveformGeneratorController:
    def __init__(self, master):
        self.master = master
        master.title("Waveform Generator Controller")

        # Detect the OS and display it
        self.os_name = platform.system()
        tk.Label(master, text=f"Operating System: {self.os_name}").grid(row=0, column=0, padx=5, pady=5, sticky="w", columnspan=2)

        # Serial port selection section using a drop-down list (Combobox)
        tk.Label(master, text="Serial Port:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.port_combo = ttk.Combobox(master, values=[], state="readonly", width=15)
        self.port_combo.grid(row=1, column=1, padx=5, pady=5)

        self.refresh_button = tk.Button(master, text="Refresh", command=self.scan_ports)
        self.refresh_button.grid(row=1, column=2, padx=5, pady=5)

        # Baud rate selection remains as an entry field
        tk.Label(master, text="Baud Rate:").grid(row=1, column=3, padx=5, pady=5, sticky="e")
        self.baud_entry = tk.Entry(master, width=10)
        self.baud_entry.grid(row=1, column=4, padx=5, pady=5)
        self.baud_entry.insert(0, "9600")  # Default baud rate

        # Connect button to open the serial port connection
        self.connect_button = tk.Button(master, text="Connect", command=self.connect)
        self.connect_button.grid(row=1, column=5, padx=5, pady=5)

        # Waveform parameters
        tk.Label(master, text="Frequency (Hz):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.freq_entry = tk.Entry(master)
        self.freq_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(master, text="Amplitude (V):").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.amp_entry = tk.Entry(master)
        self.amp_entry.grid(row=2, column=3, padx=5, pady=5)

        # Burst mode and parameter
        self.burst_var = tk.IntVar()
        self.burst_check = tk.Checkbutton(master, text="Burst Mode", variable=self.burst_var)
        self.burst_check.grid(row=3, column=0, padx=5, pady=5)

        tk.Label(master, text="Burst Parameter:").grid(row=3, column=1, padx=5, pady=5, sticky="e")
        self.burst_param_entry = tk.Entry(master)
        self.burst_param_entry.grid(row=3, column=2, padx=5, pady=5)

        # Button to send commands to the device
        self.send_button = tk.Button(master, text="Send", command=self.send_commands)
        self.send_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        # Status label to show connection and command status
        self.status_label = tk.Label(master, text="Not Connected", fg="red")
        self.status_label.grid(row=5, column=0, columnspan=6, padx=5, pady=5)

        self.serial_conn = None  # Serial connection object

        # Perform an initial scan for serial ports
        self.scan_ports()

    def scan_ports(self):
        """Scan and update the list of available serial ports."""
        ports = list(serial.tools.list_ports.comports())
        port_list = [port.device for port in ports]
        if not port_list:
            port_list = ["No ports found"]
        self.port_combo['values'] = port_list
        if port_list and port_list[0] != "No ports found":
            self.port_combo.current(0)
        else:
            self.port_combo.set("")

    def connect(self):
        """Establish a serial connection to the waveform generator."""
        port = self.port_combo.get()
        if port == "No ports found" or port == "":
            messagebox.showerror("Error", "No valid serial port selected.")
            return

        try:
            baud = int(self.baud_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid baud rate")
            return

        try:
            self.serial_conn = serial.Serial(port, baud, timeout=1)
            self.status_label.config(text=f"Connected to {port}", fg="green")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.config(text="Connection Failed", fg="red")

    def send_commands(self):
        """Compose and send commands based on user input."""
        if self.serial_conn is None or not self.serial_conn.is_open:
            messagebox.showerror("Error", "Not connected to any device")
            return

        # Retrieve and validate parameters from the GUI
        freq = self.freq_entry.get()
        amp = self.amp_entry.get()
        burst_on = self.burst_var.get()
        burst_param = self.burst_param_entry.get()

        try:
            freq_val = float(freq)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid frequency value")
            return

        try:
            amp_val = float(amp)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid amplitude value")
            return

        # Build the command strings (modify these as per your device's protocol)
        commands = []
        commands.append(f":FREQ {freq_val}")
        commands.append(f":VOLT {amp_val}")
        if burst_on:
            commands.append(":BURST:STATE ON")
            if burst_param:
                commands.append(f":BURST:PARAM {burst_param}")
        else:
            commands.append(":BURST:STATE OFF")

        # Combine commands into a single message (newline-separated)
        full_command = "\n".join(commands) + "\n"

        try:
            self.serial_conn.write(full_command.encode('utf-8'))
            self.status_label.config(text="Commands sent", fg="blue")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="Failed to send commands", fg="red")

def main():
    root = tk.Tk()
    app = WaveformGeneratorController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
