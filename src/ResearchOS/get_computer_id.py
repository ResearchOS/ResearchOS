import os, sys

def get_computer_id() -> str:
    "Method from: https://gist.github.com/angeloped/3febaaf71ac083bc2cd5d99d775921d0"
    os_type = sys.platform.lower()
    if "win" in os_type:
        command = "wmic bios get serialnumber"
    elif "linux" in os_type:
        command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
    elif "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
        
    string = os.popen(command).read().replace("\n","").replace("    ","").replace(" ","")
    
    # My modification
    if "win" in os_type:
        string = string.replace("SerialNumber","")
    elif "linux" in os_type:
        pass
    elif "darwin" in os_type:        
        string = string.replace("IOPlatformSerialNumber","").replace("=","").replace("<","").replace(">","").replace('|',"").replace(" ","").replace('"',"")
    else:
        raise ValueError("Unsupported system platform.")
        
    return string

a = get_computer_id()
COMPUTER_ID = a # To ensure the function won't be re-run.
