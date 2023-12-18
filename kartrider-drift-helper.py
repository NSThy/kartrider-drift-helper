# nsthy@hotmail.com
# depend: pip install pyautogui keyboard pygetwindow psutil
# compile: python -m PyInstaller --noupx --onefile --noconsole kartrider-drift-helper.py

################################Initialize#####################################

#Import
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import importlib
import sys
import os
import subprocess

#Variable
os_type = sys.platform

#API
def is_running_on_wayland():
    return 'WAYLAND_DISPLAY' in os.environ and os.environ['WAYLAND_DISPLAY']

def is_running_on_xorg():
    display = os.environ.get('DISPLAY')
    if display:
        return True
    else:
        return False

def check_ydotool_installed():
    try:
        subprocess.run(['which', 'ydotool'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("ydotool found.")
        return True
    except subprocess.CalledProcessError:
        print("ydotool is not installed.")
        messagebox.showerror("Error", "ydotool is not installed.")
        exit()
        return False

#Main
if os_type.startswith('win'):
	required_packages = ['pyautogui', 'keyboard', 'pygetwindow', 'psutil']
elif os_type.startswith('linux'):
	required_packages = ['pyautogui', 'keyboard', 'psutil']

missing_packages = []

for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("The following packages are missing and will be installed:", missing_packages)
    import subprocess
    subprocess.run(['pip3', 'install'] + missing_packages, check=True)
    print("Required packages installed. Please restart the script.")
    exit()
else:
    print("All python required packages are already installed.")


if os_type.startswith('win'):
    print("This is a Windows operating system.")
    # Perform actions specific to Windows
    import pygetwindow as gw
elif os_type.startswith('linux'):
    # Linux-specific code here
    print("This is a Linux operating system.")
    # Perform actions specific to Linux
    if is_running_on_wayland():
    	print("Running on Wayland session")
    	check_ydotool_installed()
    	subprocess.Popen("ydotoold", shell=True)
    elif is_running_on_xorg():
    	print("Running on Xorg session")
    else:
    	print("Unknow desktop session")
    	exit()
elif os_type == 'darwin':
    # macOS-specific code here
    print("This is a macOS operating system.")
    # Perform actions specific to macOS
    exit()
elif os_type.startswith('freebsd'):
    # FreeBSD-specific code here
    print("This is a FreeBSD operating system.")
    # Perform actions specific to FreeBSD
    exit()
else:
    print("Unsupported operating system.")
    # Handle other operating systems or unsupported cases
    messagebox.showerror("Error", "Unsupported operating system.")
    exit()


###################################Main######################################

#Import
import pyautogui
import time
import keyboard
import re
import psutil
import atexit

#Variable
window_title = "KartRider In Development"
process_name = "KartRider.exe"
key_type_speed = 0.005
sleeptime_btw_cmd = 0.5

#API
pyautogui.PAUSE = key_type_speed
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
def activate_window_by_title_windows(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)
        if len(window) > 0:
            window[0].activate()
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False
    
def activate_window_by_title_linux(title):
    try:
        # Get the window ID by its title using 'xdotool'
        window_id = subprocess.check_output(['xdotool', 'search', '--name', title]).decode().strip()
        
        # Activate the window using the window ID
        subprocess.run(['xdotool', 'windowactivate', window_id])
        return True
    except subprocess.CalledProcessError:
        return False

# check if the kartrider.exe is running
def check_process(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return True
    return False

# send the key to kartrider.exe
def send_keys(key_sequence):
    time.sleep(sleeptime_btw_cmd)
    pyautogui.press('`')
    time.sleep(sleeptime_btw_cmd)
    for key in key_sequence:
        pyautogui.write(key, interval=key_type_speed)
    pyautogui.press('enter')
    time.sleep(sleeptime_btw_cmd)
    pyautogui.press('enter')

def send_keys_linux_wayland(key_sequence):
    time.sleep(sleeptime_btw_cmd)
    subprocess.run("ydotool key 41:1 41:0", shell=True)

    parts = key_sequence.split('_')
    before_underscore = parts[0]
    after_underscore = parts[1] if len(parts) > 1 else ""
    
    time.sleep(sleeptime_btw_cmd)
    subprocess.run(f"ydotool type \"{before_underscore}\"", shell=True)

    if "_" in key_sequence:
    	subprocess.run(f"ydotool key 42:1 12:1 12:0 42:0", shell=True)

    subprocess.run(f"ydotool type \"{after_underscore}\"", shell=True)
    subprocess.run("ydotool key 28:1 28:0", shell=True)
    time.sleep(sleeptime_btw_cmd)
    subprocess.run("ydotool key 28:1 28:0", shell=True)

# double click on list box item
def on_double_click(event):
    widget = event.widget
    unconvert_selected_item = widget.get(widget.curselection())
    selected_item=re.search(r'\[(.*?)\]', unconvert_selected_item).group(1)
    print(f"Double-clicked on: {selected_item}")
    print("Performing open map action...")
        
    if check_process(process_name):
    	if os_type.startswith('win'):
        	if activate_window_by_title_windows(window_title):
                	send_keys(f"open {selected_item}")
                	activate_window_by_title_windows("Kartrider drift helper")
        	else: 
                	print(f"Window '{window_title}' not found.")
                	messagebox.showerror("Error", f"Window '{window_title}' not found.")
    	elif os_type.startswith('linux'):   
        	if activate_window_by_title_linux(window_title):
                	if is_running_on_wayland():
                        	send_keys_linux_wayland(f"open {selected_item}")
                	else:
                        	send_keys(f"open {selected_item}")
                        
                	activate_window_by_title_linux("Kartrider drift helper")
        	else: 
                	print(f"Window '{window_title}' not found.")
                	messagebox.showerror("Error", f"Window '{window_title}' not found.")
            
    else:
        print(f"Process '{process_name}' is not running.")
        messagebox.showerror("Error", f"Process '{process_name}' is not running.")

def terminate_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.terminate()
            print(f"Process '{process_name}' terminated.")
            return True
    print(f"Process '{process_name}' not found.")
    return False

def terminate_process():
	terminate_process_by_name(process_name)
	if os_type.startswith('win'):
		terminate_process_by_name(process_name)
	elif os_type.startswith('linux'):
		terminate_process_by_name("CrBrowserMain")

def start_program():
    program_path = os.path.join(os.path.dirname(__file__), "KartRider.exe")

    try:
        if not check_process(process_name):
            subprocess.Popen(program_path)
            print("Program started successfully!")
        else:
            print("Program already started!")
    except Exception as e:
        print(f"Failed to start program: {e},please put this script in the same directory")
        messagebox.showerror("Error", "Failed to start program: KartRider.exe,please put this script in the same directory")

def start_race():
    if check_process(process_name):
    	if os_type.startswith('win'):
        	if activate_window_by_title_windows(window_title):
                	send_keys('r.GPUBusyWait 0')
                	send_keys('Dev_ResetRace 3')
        	else: 
                	print(f"Window '{window_title}' not found.")
                	messagebox.showerror("Error", f"Window '{window_title}' not found.")
    	elif os_type.startswith('linux'):   
        	if activate_window_by_title_linux(window_title):
                	if is_running_on_wayland():
                        	send_keys_linux_wayland('r.GPUBusyWait 0')
                        	send_keys_linux_wayland('Dev_ResetRace 3')
                	else:
                        	send_keys('r.GPUBusyWait 0')
                        	send_keys('Dev_ResetRace 3')
        	else: 
                	print(f"Window '{window_title}' not found.")
                	messagebox.showerror("Error", f"Window '{window_title}' not found.")
            
    else:
            print(f"Process '{process_name}' is not running.")
            messagebox.showerror("Error", f"Process '{process_name}' is not running.")

def on_exit():
    if os_type.startswith('linux') and is_running_on_wayland():
    	terminate_process_by_name("ydotoold")

#Main
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

    if not os_type.startswith('win'):
    	button_start.config(state=tk.DISABLED)

    button_middle = tk.Button(root, text="Start Race", command=start_race)
    button_middle.place(relx=0.5, rely=0.855, anchor=tk.CENTER)

    button_terminate = tk.Button(root, text="Stop", command=terminate_process)
    button_terminate.pack(side=tk.RIGHT, padx=10, pady=20)
        
    tooltip_text = "Make sure the map is loaded!"
    tooltip = ToolTip(button_middle, tooltip_text)

    atexit.register(on_exit)
    
    root.mainloop()

if __name__ == "__main__":
    main()
