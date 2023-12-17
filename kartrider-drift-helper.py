import importlib

required_packages = ['pyautogui', 'keyboard', 'pygetwindow', 'psutil']
missing_packages = []

for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("The following packages are missing and will be installed:", missing_packages)
    import subprocess
    subprocess.run(['pip', 'install'] + missing_packages, check=True)
    print("Required packages installed. Please restart the script.")
else:
    print("All required packages are already installed.")

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyautogui
import time
import keyboard
import re
import pygetwindow as gw
import psutil
import subprocess
import os

# depend: pip install pyautogui keyboard pygetwindow psutil
# compile: python -m PyInstaller --noupx --onefile --noconsole kartrider-drift-helper.py

window_title = "KartRider In Development"
process_name = "KartRider.exe"
pyautogui.PAUSE = 0.005

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.display_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def display_tooltip(self, event):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty() - 5

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief='solid', borderwidth=1)
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()


# switch to the kartrider window
def activate_window_by_title(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)
        if len(window) > 0:
            window[0].activate()
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

# check if the kartrider.exe is running
def check_process(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return True
    return False

# send the key to kartrider.exe
def send_keys(key_sequence):
    pyautogui.press('`')
    time.sleep(0.1)
    for key in key_sequence:
        pyautogui.write(key, interval=0.005)
    pyautogui.press('enter')
    pyautogui.press('enter')

# double click on list box item
def on_double_click(event):
    widget = event.widget
    unconvert_selected_item = widget.get(widget.curselection())
    selected_item=re.search(r'\[(.*?)\]', unconvert_selected_item).group(1)
    print(f"Double-clicked on: {selected_item}")
    print("Performing open map action...")
        
    if check_process(process_name):
        if activate_window_by_title(window_title):
            send_keys(f"open {selected_item}")
            activate_window_by_title("Kartrider drift helper")
        else: 
            print(f"Window '{window_title}' not found.")
            messagebox.showerror("Error", f"Window '{window_title}' not found.")
    else:
        print(f"Process '{process_name}' is not running.")
        messagebox.showerror("Error", f"Process '{process_name}' is not running.")

def terminate_process():
    process_terminated = False

    # Find process by window title
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process = psutil.Process(proc.info['pid'])
            if process.name().lower() == "kartrider.exe":
                if process.exe().lower().endswith("kartrider.exe"):
                    process_terminated = True
                    process.terminate()
                    process.terminate()
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if process_terminated:
        print("Process terminated successfully!")
    else:
        print("Process not found!")

def start_program():
    program_path = os.path.join(os.path.dirname(__file__), "KartRider.exe")

    try:
        if not check_process(process_name):
            subprocess.Popen(program_path)
            print("Program started successfully!")
        else:
            print("Program already started!")
    except Exception as e:
        print(f"Failed to start program: {e}")
        messagebox.showerror("Failed to start program: KartRider.exe")

def start_race():
    if check_process(process_name):
        if activate_window_by_title(window_title):
            send_keys('r.GPUBusyWait 0')
            send_keys('Dev_ResetRace 3')
        else:
            print(f"Window '{window_title}' not found.")
            messagebox.showerror("Error", f"Window '{window_title}' not found.")
    else:
            print(f"Process '{process_name}' is not running.")
            messagebox.showerror("Error", f"Process '{process_name}' is not running.")

def main():
    root = tk.Tk()
    root.title("Kartrider drift helper")
    root.resizable(False, False)
    
    frame = tk.Frame(root)
    frame.pack()

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    
    listbox = tk.Listbox(frame, width=30, yscrollcommand=scrollbar.set)

    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    items = ["[village_R01]城镇高速公路", "[village_R03]城镇R03", "[village_I04]城镇运河", "[village_I02]城镇手指", "[forest_I04]奇石", "[forest_I03]山谷", "[forest_I01]森林木桶", "[desert_I02]金字塔", "[desert_R01]沙漠R01", "[desert_R02]沙漠R02", "[ice_I04]冰山I01", "[ice_I05]冰山急速", "[ice_R04]冰山R04", "[tomb_I01]幽灵I01", "[tomb_I02]幽灵I02", "[tomb_I04]幽灵I04", "[moonhill_I04]月球I04", "[moonhill_I03]月球I03", "[moonhill_I02]月球I02", "[beach_R01]沙滩", "[world_R02]里约", "[world_R12]长城"]
    for item in items:
        listbox.insert(tk.END, item)

    listbox.bind("<Double-Button-1>", on_double_click)
    listbox.pack()

    button_start = tk.Button(root, text="Run", command=start_program)
    button_start.pack(side=tk.LEFT, padx=10, pady=20)

    button_middle = tk.Button(root, text="Start Race", command=start_race)
    button_middle.place(relx=0.5, rely=0.855, anchor=tk.CENTER)

    button_terminate = tk.Button(root, text="Stop", command=terminate_process)
    button_terminate.pack(side=tk.RIGHT, padx=10, pady=20)
    
    tooltip_text = "Make sure the map is loaded!"
    tooltip = ToolTip(button_middle, tooltip_text)

    root.mainloop()

if __name__ == "__main__":
    main()
