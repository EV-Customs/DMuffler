#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "2025.0"
__doc__        = "Connect DMuffler Dongle to iPhone and Android devices via Bluetooth"
"""

from bluepy.btle import Scanner, DefaultDelegate, Peripheral
import time
from logging_utils import log_info, log_warning, log_error

""" On Raspberry Pi CM4 or Raspberry Pi 500
sudo apt-get update
sudo apt-get install python3-pip python3-dev bluetooth bluez bluez-tools rfcomm
pip3 install bluepy

Standard Bluetooth SPP (Serial Port Profile 'import bluetooth') isn't fully supported on iOS. You'll likely need to use Bluetooth Low Energy (BLE)

sudo nano /etc/bluetooth/main.conf
> DiscoverableTimeout = 0
> PairableTimeout = 0
sudo systemctl restart bluetooth

sudo bluetoothctl
Within bluetoothctl, run:
```
power on
discoverable on
pairable on
agent on
default-agent
```
"""
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            log_info(f"Discovered device: {dev.addr}")

def connect_with_retry(dev, addr_type, retries=3, delay=1):
    for _ in range(retries):
        try:
            peripheral = Peripheral(dev.addr, addr_type)
            return peripheral
        except Exception as e:
            log_error(f"Error connecting to {dev.addr}: {e}")
            time.sleep(delay)
    return None

# Scan for devices
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)

# Find your iPhone
iphone_dev = None
for dev in devices:
    log_info(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
    for (adtype, desc, value) in dev.getScanData():
        log_info(f"  {desc} = {value}")
    if "iPhone" in dev.getValueText(9) or "iPhone" in str(dev.getScanData()):  # Check device name
        iphone_dev = dev
        log_info("Found iPhone!")

if iphone_dev:
    log_info(f"Connecting to {iphone_dev.addr}...")
    peripheral = connect_with_retry(iphone_dev, iphone_dev.addrType)
    if peripheral:
        try:
            # Discover services
            services = peripheral.getServices()
        except Exception as e:
            log_error(f"Error: {e}")
        finally:
            peripheral.disconnect()
    else:
        log_warning("Failed to connect to iPhone")
else:
    log_warning("iPhone not found")
