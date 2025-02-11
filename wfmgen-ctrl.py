#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import serial
import serial.tools.list_ports

class WaveformGeneratorController:
    def __init__(self, master):
        self.master = master
        master.title("Contrôleur de Générateur de Signaux")

        # Ligne 0 : Affichage du système d'exploitation
        self.os_name = platform.system()
        tk.Label(master, text=f"Système d'exploitation: {self.os_name}")\
            .grid(row=0, column=0, padx=5, pady=5, sticky="w", columnspan=7)

        # Ligne 1 : Port série, rafraîchir, baud rate, connexion/déconnexion
        tk.Label(master, text="Port Série:")\
            .grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.port_combo = ttk.Combobox(master, values=[], state="readonly", width=15)
        self.port_combo.grid(row=1, column=1, padx=5, pady=5)
        self.refresh_button = tk.Button(master, text="Rafraîchir", command=self.scan_ports)
        self.refresh_button.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Label(master, text="Baud Rate:")\
            .grid(row=1, column=3, padx=5, pady=5, sticky="e")
        self.baud_entry = tk.Entry(master, width=10)
        self.baud_entry.grid(row=1, column=4, padx=5, pady=5)
        self.baud_entry.insert(0, "9600")  # Valeur par défaut

        self.connect_button = tk.Button(master, text="Connecter", command=self.connect)
        self.connect_button.grid(row=1, column=5, padx=5, pady=5)
        self.disconnect_button = tk.Button(master, text="Déconnecter", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.grid(row=1, column=6, padx=5, pady=5)

        # Ligne 2 : Sélection du type de signal
        tk.Label(master, text="Type de signal:")\
            .grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.signal_type_combo = ttk.Combobox(master, values=["Sinus", "Carré", "Triangle", "Impulsion"],
                                              state="readonly", width=15)
        self.signal_type_combo.grid(row=2, column=1, padx=5, pady=5)
        self.signal_type_combo.set("Sinus")  # Valeur par défaut

        # Ligne 3 : Paramètres du signal (Fréquence et Amplitude)
        tk.Label(master, text="Fréquence (kHz):")\
            .grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.freq_entry = tk.Entry(master)
        self.freq_entry.grid(row=3, column=1, padx=5, pady=5)
        self.freq_entry.insert(0, "5000")  # 5 MHz = 5000 kHz

        tk.Label(master, text="Amplitude (V):")\
            .grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.amp_entry = tk.Entry(master)
        self.amp_entry.grid(row=3, column=3, padx=5, pady=5)
        self.amp_entry.insert(0, "1")  # Valeur par défaut : 1 V

        # Ligne 4 : Mode Burst et ses paramètres
        self.burst_var = tk.IntVar()
        self.burst_check = tk.Checkbutton(master, text="Mode Burst", variable=self.burst_var,
                                          command=self.toggle_burst_controls)
        self.burst_check.grid(row=4, column=0, padx=5, pady=5)
        
        tk.Label(master, text="Nombre de cycles:")\
            .grid(row=4, column=1, padx=5, pady=5, sticky="e")
        self.cycle_entry = tk.Entry(master)
        self.cycle_entry.grid(row=4, column=2, padx=5, pady=5)
        self.cycle_entry.insert(0, "10")  # Valeur par défaut : 10 cycles
        self.cycle_entry.config(state=tk.DISABLED)
        
        tk.Label(master, text="Délai du burst (us):")\
            .grid(row=4, column=3, padx=5, pady=5, sticky="e")
        self.delay_entry = tk.Entry(master)
        self.delay_entry.grid(row=4, column=4, padx=5, pady=5)
        self.delay_entry.insert(0, "1")  # Valeur par défaut : 1 us
        self.delay_entry.config(state=tk.DISABLED)

        # Ligne 5 : Sélection du trigger (disponible uniquement si Mode Burst est coché)
        tk.Label(master, text="Type de trigger:")\
            .grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.trigger_combo = ttk.Combobox(master, values=["Interne", "Externe"],
                                          state="disabled", width=15)
        self.trigger_combo.grid(row=5, column=1, padx=5, pady=5)
        self.trigger_combo.set("Externe")  # Valeur par défaut

        # Ligne 6 : Bouton pour envoyer les commandes
        self.send_button = tk.Button(master, text="Envoyer", command=self.send_commands, state=tk.DISABLED)
        self.send_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        # Ligne 7 : Label d'état
        self.status_label = tk.Label(master, text="Non connecté", fg="red")
        self.status_label.grid(row=7, column=0, columnspan=7, padx=5, pady=5)

        self.serial_conn = None  # Objet de connexion série
        self.scan_ports()  # Premier balayage des ports disponibles

    def toggle_burst_controls(self):
        """Active ou désactive les champs des paramètres burst et du trigger en fonction de l'état du mode burst."""
        if self.burst_var.get():
            self.cycle_entry.config(state=tk.NORMAL)
            self.delay_entry.config(state=tk.NORMAL)
            self.trigger_combo.config(state="readonly")
        else:
            self.cycle_entry.config(state=tk.DISABLED)
            self.delay_entry.config(state=tk.DISABLED)
            self.trigger_combo.config(state="disabled")
            self.cycle_entry.delete(0, tk.END)
            self.cycle_entry.insert(0, "10")  # Réinitialise à la valeur par défaut
            self.delay_entry.delete(0, tk.END)
            self.delay_entry.insert(0, "1")   # Réinitialise à la valeur par défaut
            self.trigger_combo.set("Externe")  # Réinitialise à la valeur par défaut

    def scan_ports(self):
        """Recherche et met à jour la liste des ports série disponibles."""
        ports = list(serial.tools.list_ports.comports())
        port_list = [port.device for port in ports]
        if not port_list:
            port_list = ["Aucun port trouvé"]
        self.port_combo['values'] = port_list
        if port_list and port_list[0] != "Aucun port trouvé":
            self.port_combo.current(0)
        else:
            self.port_combo.set("")

    def connect(self):
        """Établit la connexion série avec le générateur de signaux."""
        port = self.port_combo.get()
        if port == "Aucun port trouvé" or port == "":
            messagebox.showerror("Erreur", "Aucun port série valide sélectionné.")
            return

        try:
            baud = int(self.baud_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Débit en bauds invalide.")
            return

        try:
            self.serial_conn = serial.Serial(port, baud, timeout=1)
            self.status_label.config(text=f"Connecté à {port}", fg="green")
            # Mise à jour des boutons
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.DISABLED)
            self.send_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Erreur de connexion", str(e))
            self.status_label.config(text="Échec de connexion", fg="red")

    def disconnect(self):
        """Ferme la connexion série."""
        if self.serial_conn is not None and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None
            self.status_label.config(text="Déconnecté", fg="orange")
            # Mise à jour des boutons
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Info", "Aucune connexion active à déconnecter.")

    def send_commands(self):
        """Compose et envoie les commandes SCPI en fonction des paramètres saisis."""
        if self.serial_conn is None or not self.serial_conn.is_open:
            messagebox.showerror("Erreur", "Non connecté à un appareil.")
            return

        commands = []

        # Ajout de la commande pour le type de signal
        signal_type = self.signal_type_combo.get()
        signal_map = {"Sinus": "SIN", "Carré": "SQU", "Triangle": "TRI", "Impulsion": "PULS"}
        if signal_type in signal_map:
            commands.append(f":FUNC {signal_map[signal_type]}")

        # Récupération et validation des paramètres du signal
        freq = self.freq_entry.get()
        amp = self.amp_entry.get()
        burst_on = self.burst_var.get()

        try:
            freq_val = float(freq)
            # Conversion de kHz en Hz
            freq_val *= 1000
        except ValueError:
            messagebox.showerror("Erreur de saisie", "Valeur de fréquence invalide.")
            return

        try:
            amp_val = float(amp)
        except ValueError:
            messagebox.showerror("Erreur de saisie", "Valeur d'amplitude invalide.")
            return

        commands.append(f":FREQ {freq_val}")
        commands.append(f":VOLT {amp_val}")

        if burst_on:
            commands.append(":BURST:STATE ON")
            # Nombre de cycles
            cycle = self.cycle_entry.get().strip()
            if not cycle:
                messagebox.showerror("Erreur de saisie", "Veuillez spécifier le nombre de cycles pour le mode burst.")
                return
            try:
                cycle_val = int(cycle)
                commands.append(f":BURST:NCYC {cycle_val}")
            except ValueError:
                messagebox.showerror("Erreur de saisie", "Nombre de cycles invalide.")
                return

            # Délai du burst
            delay = self.delay_entry.get().strip()
            if not delay:
                messagebox.showerror("Erreur de saisie", "Veuillez spécifier le délai du burst.")
                return
            try:
                delay_val = float(delay)
                commands.append(f":BURST:DELay {delay_val}")
            except ValueError:
                messagebox.showerror("Erreur de saisie", "Délai du burst invalide.")
                return

            # Ajout de la commande pour le trigger (uniquement si le mode burst est activé)
            trigger_type = self.trigger_combo.get()
            trigger_map = {"Interne": "INT", "Externe": "EXT"}
            if trigger_type in trigger_map:
                commands.append(f":TRIG:SOUR {trigger_map[trigger_type]}")
        else:
            commands.append(":BURST:STATE OFF")

        full_command = "\n".join(commands) + "\n"

        try:
            self.serial_conn.write(full_command.encode('utf-8'))
            self.status_label.config(text="Commandes envoyées", fg="blue")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.status_label.config(text="Échec d'envoi des commandes", fg="red")

def main():
    root = tk.Tk()
    app = WaveformGeneratorController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
