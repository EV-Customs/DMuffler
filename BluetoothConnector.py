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
            print(f"Discovered device: {dev.addr}")

# Scan for devices
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)

# Find your iPhone
iphone_dev = None
for dev in devices:
    print(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
    for (adtype, desc, value) in dev.getScanData():
        print(f"  {desc} = {value}")
    if "iPhone" in dev.getValueText(9) or "iPhone" in str(dev.getScanData()):  # Check device name
        iphone_dev = dev
        print("Found iPhone!")

if iphone_dev:
    try:
        print(f"Connecting to {iphone_dev.addr}...")
        peripheral = Peripheral(iphone_dev.addr, iphone_dev.addrType)

        # Discover services
        services = peripheral.getServices()
        for service in services:
            print(f"Service: {service.uuid}")
            characteristics = service.getCharacteristics()
            for char in characteristics:
                print(f"  Characteristic: {char.uuid}")

        # You would need to know the specific UUID of the characteristic to read or write
        # Example (you'll need to replace with a valid UUID):
        # char = peripheral.getCharacteristics(uuid="UUID")[0]
        # char.write(bytes("Hello from Pi", "utf-8"))

        peripheral.disconnect()
    except Exception as e:
        print(f"Error: {e}")
else:
    print("iPhone not found")
