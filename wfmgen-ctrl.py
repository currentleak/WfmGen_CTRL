class WaveformGeneratorController:
    def __init__(self, master):
        self.master = master
        master.title("Waveform Generator Controller")

        # Connection settings
        tk.Label(master, text="COM Port:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.port_entry = tk.Entry(master)
        self.port_entry.grid(row=0, column=1, padx=5, pady=5)
        self.port_entry.insert(0, "COM3")  # Set a default COM port (adjust as needed)

        tk.Label(master, text="Baud Rate:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.baud_entry = tk.Entry(master)
        self.baud_entry.grid(row=0, column=3, padx=5, pady=5)
        self.baud_entry.insert(0, "9600")  # Default baud rate

        self.connect_button = tk.Button(master, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        # Waveform parameters
        tk.Label(master, text="Frequency (Hz):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.freq_entry = tk.Entry(master)
        self.freq_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(master, text="Amplitude (V):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.amp_entry = tk.Entry(master)
        self.amp_entry.grid(row=1, column=3, padx=5, pady=5)

        # Burst mode option
        self.burst_var = tk.IntVar()
        self.burst_check = tk.Checkbutton(master, text="Burst Mode", variable=self.burst_var)
        self.burst_check.grid(row=2, column=0, padx=5, pady=5)

        tk.Label(master, text="Burst Parameter:").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        self.burst_param_entry = tk.Entry(master)
        self.burst_param_entry.grid(row=2, column=2, padx=5, pady=5)

        # Send command button
        self.send_button = tk.Button(master, text="Send", command=self.send_commands)
        self.send_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Status label
        self.status_label = tk.Label(master, text="Not Connected", fg="red")
        self.status_label.grid(row=4, column=0, columnspan=5, padx=5, pady=5)

        self.serial_conn = None  # Serial connection object

    def connect(self):
        """Establish a serial connection to the waveform generator."""
        port = self.port_entry.get()
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

        # Retrieve parameters from the GUI
        freq = self.freq_entry.get()
        amp = self.amp_entry.get()
        burst_on = self.burst_var.get()
        burst_param = self.burst_param_entry.get()

        # Validate numeric inputs
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

        # Build command strings (adjust these commands as per your device's protocol)
        commands = []
        commands.append(f":FREQ {freq_val}")
        commands.append(f":VOLT {amp_val}")
        if burst_on:
            commands.append(":BURST:STATE ON")
            if burst_param:
                # This is a placeholder command for a burst parameter (e.g., burst count, width, etc.)
                commands.append(f":BURST:PARAM {burst_param}")
        else:
            commands.append(":BURST:STATE OFF")

        # Combine commands into one message (separated by newline if your device accepts multiple commands)
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
