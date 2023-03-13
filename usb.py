import os
import shutil

usb_path = os.getcwd()  # Get the current directory of the script (USB drive)
desktop_path = os.path.join(os.path.expanduser("~"), "Documents")  # Get the desktop path

for file in os.listdir(usb_path):
    file_path = os.path.join(usb_path, file)
    if os.path.isfile(file_path):
        shutil.copy2(file_path, desktop_path)
