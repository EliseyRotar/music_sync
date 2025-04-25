import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from threading import Thread
import time
import hashlib
import json
import socket
import ipaddress
import ttkbootstrap as tb

SETTINGS_FILE = os.path.expanduser("~/.music_sync_settings.json")
LOCAL_DIR_DEFAULT = os.path.expanduser("~/Spotube")
DEVICE_DIR = "/sdcard/Music"
current_device = None

# Tooltip helper
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.overrideredirect(True)
        self.tooltip.geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("Arial", 9)
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def get_local_subnet():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return str(ipaddress.IPv4Network(local_ip + "/24", strict=False))

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {
        "local_dir": LOCAL_DIR_DEFAULT,
        "theme": "darkly",
        "auto_connect_ips": [],
        "scan_range": ""
    }

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

settings = load_settings()

class MusicSyncApp(tb.Window):
    def __init__(self):
        super().__init__(themename=settings.get("theme", "darkly"))
        self.title("Music Sync App")
        self.geometry("650x600")
        self.create_widgets()
        self.current_process = None
        self.is_running = False
        self.should_stop = False
        self.local_dir = settings.get("local_dir", LOCAL_DIR_DEFAULT)

        # Ask for scan range if missing
        if not settings.get("scan_range"):
            self.prompt_for_ip_range()

        # Auto-connect
        if settings.get("auto_connect_ips"):
            for ip in settings["auto_connect_ips"]:
                self.connect_to_device_wifi(ip)

    def prompt_for_ip_range(self):
        def is_valid_range(ip_range):
            try:
                ipaddress.IPv4Network(ip_range)
                return True
            except ValueError:
                return False

        default_range = get_local_subnet()

        while not settings.get("scan_range"):
            response = simpledialog.askstring(
                "Network Scan Range",
                "Enter your network range (e.g., 192.168.1.0/24):",
                initialvalue=default_range
            )
            if response is None:
                messagebox.showerror("Required", "You must enter a valid IP range to continue.")
            elif is_valid_range(response.strip()):
                settings["scan_range"] = response.strip()
                save_settings(settings)
                break
            else:
                messagebox.showerror("Invalid", "Invalid IP range. Try again.")

    def create_widgets(self):
        self.device_label = ttk.Label(self, text="No device connected", font=("Arial", 12))
        self.device_label.pack(pady=5)

        ttk.Button(self, text="Scan for Devices", command=lambda: self.run_thread(self.scan_for_devices)).pack(pady=5)
        ttk.Button(self, text="Check ADB Connection", command=lambda: self.run_thread(self.check_adb)).pack(pady=5)
        ttk.Button(self, text="Sync Only New Songs", command=lambda: self.run_thread(self.sync_new_songs)).pack(pady=5)
        ttk.Button(self, text="Clear and Sync", command=lambda: self.run_thread(self.clear_and_sync)).pack(pady=5)
        ttk.Button(self, text="Delete Only Music Files", command=lambda: self.run_thread(self.delete_music)).pack(pady=5)

        self.stop_button = ttk.Button(self, text="Stop", state="disabled", command=self.stop_task)
        self.stop_button.pack(pady=5)

        ttk.Button(self, text="Settings", command=self.show_settings_panel).pack(pady=5)
        ttk.Button(self, text="Exit", command=self.destroy).pack(pady=5)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)

        self.console = tk.Text(self, height=10, width=80, state="disabled", bg="#f0f0f0")
        self.console.pack(pady=10)
        self.log("App started.")

    def log(self, text):
        self.console.config(state="normal")
        self.console.insert(tk.END, f"{text}\n")
        self.console.see(tk.END)
        self.console.config(state="disabled")

    def run_thread(self, func):
        def wrapper():
            if not self.is_running:
                self.is_running = True
                self.should_stop = False
                self.stop_button.config(state="normal")
                try:
                    func()
                except Exception as e:
                    self.log(f"[ERROR] {e}")
                    messagebox.showerror("Error", str(e))
                self.is_running = False
                self.stop_button.config(state="disabled")
            else:
                messagebox.showinfo("Task Running", "A task is already running.")
        Thread(target=wrapper, daemon=True).start()

    def stop_task(self):
        self.should_stop = True
        if self.current_process:
            self.current_process.terminate()
            self.current_process = None
            self.log("[INFO] Task was stopped.")
        self.status_label.config(text="Task stopped.")
        self.progress["value"] = 0
        self.stop_button.config(state="disabled")

    def get_device_id(self):
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        for line in result.stdout.splitlines()[1:]:
            if "device" in line:
                return line.split()[0]
        return None

    def check_device(self):
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        return any("device" in line for line in result.stdout.splitlines()[1:])

    def check_adb(self):
        self.status_label.config(text="Checking ADB connection...")
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        if len(lines) > 1 and any("device" in line for line in lines[1:]):
            device_id = self.get_device_id()
            ip = subprocess.run(["adb", "-s", device_id, "shell", "ip", "route"], capture_output=True, text=True).stdout.split()[8]
            device_name = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
            self.device_label.config(text=f"Connected to: {ip} ({device_name})")
            messagebox.showinfo("ADB Connection", f"Connected to {ip} ({device_name})")
            self.log(f"Connected to {ip} ({device_name})")
        else:
            self.device_label.config(text="No device connected.")
            messagebox.showerror("ADB", "No ADB device connected.")
        self.status_label.config(text="")

    def get_local_files(self):
        return [f for f in os.listdir(self.local_dir) if f.endswith((".m4a", ".mp3"))]

    def get_device_files(self):
        device_id = self.get_device_id()
        result = subprocess.run(["adb", "-s", device_id, "shell", f"ls {DEVICE_DIR}"], capture_output=True, text=True)
        return result.stdout.splitlines() if result.returncode == 0 else []

    def file_hash(self, path):
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def sync_new_songs(self):
        if not self.check_device(): return
        local_files = self.get_local_files()
        device_files = self.get_device_files()
        new_files = [f for f in local_files if f not in device_files]
        if not new_files:
            messagebox.showinfo("Sync", "All songs are already synced.")
            return

        self.progress["maximum"] = len(new_files)
        self.progress["value"] = 0

        for i, file in enumerate(new_files):
            if self.should_stop: break
            full_path = os.path.join(self.local_dir, file)
            self.status_label.config(text=f"Syncing {file}...")
            self.log(f"Pushing: {file}")
            start_time = time.time()
            self.current_process = subprocess.Popen(["adb", "push", full_path, DEVICE_DIR])
            self.current_process.wait()
            speed = os.path.getsize(full_path) / 1024 / (time.time() - start_time)
            self.log(f"{file} transferred at {speed:.2f} KB/s")
            self.progress["value"] = i + 1

        self.status_label.config(text="Sync complete.")
        self.log("Sync complete.")
        messagebox.showinfo("Sync", "New songs synced successfully.")

    def clear_and_sync(self):
        if not self.check_device(): return
        if not messagebox.askyesno("Clear and Sync", "This will delete all music before syncing. Continue?"):
            return
        self.status_label.config(text="Clearing device...")
        self.log("Clearing device music files...")
        subprocess.run(["adb", "shell", f"rm -rf {DEVICE_DIR}/*"])
        self.sync_new_songs()

    def delete_music(self):
        if not self.check_device(): return
        if not messagebox.askyesno("Delete Music", "Delete all music files from device?"):
            return
        self.status_label.config(text="Deleting music files...")
        self.log("Deleting all music files from device.")
        subprocess.run(["adb", "shell", f"rm -rf {DEVICE_DIR}/*"])
        self.status_label.config(text="Music files deleted.")
        self.log("Music files deleted.")
        messagebox.showinfo("Delete", "Music deleted.")

    def scan_for_devices(self):
        try:
            ip_range = settings.get("scan_range", get_local_subnet())
            self.status_label.config(text="Scanning...")
            self.log(f"Running nmap scan on {ip_range}...")
            result = subprocess.run(["nmap", "-p", "5555", "--open", ip_range], capture_output=True, text=True)
            devices = [line.split()[-1] for line in result.stdout.splitlines() if "Nmap scan report" in line]
            if devices:
                self.show_device_selection(devices)
            else:
                messagebox.showerror("Scan", "No devices with ADB over Wi-Fi found.")
        except Exception as e:
            self.log(f"[ERROR] Scan failed: {e}")
            messagebox.showerror("Scan Error", str(e))

    def show_device_selection(self, devices):
        window = tk.Toplevel(self)
        window.title("Select Device")
        ttk.Label(window, text="Choose a device:").pack(pady=5)
        listbox = tk.Listbox(window)
        for d in devices:
            listbox.insert(tk.END, d)
        listbox.pack(pady=5)

        def connect():
            ip = listbox.get(tk.ACTIVE)
            if ip:
                self.connect_to_device_wifi(ip)
                if ip not in settings["auto_connect_ips"]:
                    settings["auto_connect_ips"].append(ip)
                    save_settings(settings)
                window.destroy()
        ttk.Button(window, text="Connect", command=connect).pack(pady=5)

    def connect_to_device_wifi(self, ip):
        global current_device
        try:
            self.log(f"Connecting to {ip}...")
            subprocess.run(["adb", "disconnect"])
            subprocess.run(["adb", "connect", f"{ip}:5555"], check=True)
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            if any(ip in line and "device" in line for line in result.stdout.splitlines()):
                device_name = subprocess.run(["adb", "-s", ip, "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
                current_device = ip
                self.device_label.config(text=f"Connected to: {ip} ({device_name})")
                self.status_label.config(text="Connected")
                self.stop_button.config(state="normal")
                self.log(f"Connected to {ip} ({device_name})")
            else:
                raise RuntimeError("Device not found in ADB list.")
        except Exception as e:
            self.log(f"[ERROR] Connection failed: {e}")
            messagebox.showerror("Connection Error", str(e))
            self.device_label.config(text="No device connected.")

    def show_settings_panel(self):
        window = tk.Toplevel(self)
        window.title("Settings")

        ttk.Label(window, text="Local Music Folder:").pack(pady=5)
        folder_label = ttk.Label(window, text=self.local_dir)
        folder_label.pack(pady=2)

        def change_folder():
            folder = filedialog.askdirectory()
            if folder:
                self.local_dir = folder
                settings["local_dir"] = folder
                folder_label.config(text=folder)
                save_settings(settings)
        ttk.Button(window, text="Change Folder", command=change_folder).pack(pady=5)

        def toggle_theme():
            new_theme = "flatly" if self.style.theme.name == "darkly" else "darkly"
            self.style.theme_use(new_theme)
            settings["theme"] = new_theme
            save_settings(settings)
        ttk.Button(window, text="Toggle Theme", command=toggle_theme).pack(pady=5)

        def clear_ips():
            settings["auto_connect_ips"] = []
            save_settings(settings)
            messagebox.showinfo("Cleared", "Auto-connect IPs cleared.")
        ttk.Button(window, text="Clear Auto-Connect IPs", command=clear_ips).pack(pady=5)

        # Scan range input with tooltip
        frame = ttk.Frame(window)
        frame.pack(pady=5)
        ttk.Label(frame, text="Network Scan Range:").pack(side="left")

        info_icon = ttk.Label(frame, text=" (?) ", foreground="blue", cursor="question_arrow")
        info_icon.pack(side="left", padx=5)

        ToolTip(info_icon,
            "This is the IP range used to scan for Android devices with ADB over Wi-Fi.\n"
            "Example: 192.168.1.0/24\n\n"
            "To find your range:\n"
            " • On Windows: run 'ipconfig'\n"
            " • On Linux/Mac: run 'ifconfig'"
        )

        scan_entry = ttk.Entry(window)
        scan_entry.insert(0, settings.get("scan_range", get_local_subnet()))
        scan_entry.pack(pady=5)

        def save_scan_range():
            value = scan_entry.get().strip()
            try:
                ipaddress.IPv4Network(value)
                settings["scan_range"] = value
                save_settings(settings)
                messagebox.showinfo("Saved", "Scan range updated.")
            except ValueError:
                messagebox.showerror("Invalid", "Invalid IP range format.")
        ttk.Button(window, text="Save Scan Range", command=save_scan_range).pack(pady=5)

if __name__ == "__main__":
    app = MusicSyncApp()
    app.mainloop()
