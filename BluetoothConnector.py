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
    """
    Delegate class to handle Bluetooth Low Energy (BLE) device discovery events.
    Inherits from bluepy.btle.DefaultDelegate.
    """
    def __init__(self):
        """Initializes the ScanDelegate instance."""
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        """
        Handles a device discovery event.

        Args:
            dev: The discovered bluepy.btle.ScanEntry object.
            isNewDev (bool): True if this is the first time the device is seen.
            isNewData (bool): True if new advertising data is available for this device.
        """
        if isNewDev:
            log_info(f"Discovered device: {dev.addr}")

def connect_with_retry(dev, addr_type, retries=3, delay=1):
    """
    Attempts to connect to a BLE device with multiple retries.

    Args:
        dev: The bluepy.btle.ScanEntry object representing the device to connect to.
        addr_type (str): The address type of the device (e.g., 'public', 'random').
        retries (int): The number of connection attempts.
        delay (int): The delay in seconds between retries.

    Returns:
        bluepy.btle.Peripheral: The connected peripheral object on success, or None on failure.
    """
    for i in range(retries):
        try:
            log_info(f"Attempting to connect to {dev.addr} (Attempt {i+1}/{retries})...")
            peripheral = Peripheral(dev.addr, addr_type)
            return peripheral
        except Exception as e:
            log_error(f"Error connecting to {dev.addr}: {e}")
            time.sleep(delay)
    return None

if __name__ == "__main__":
    devices = [] # Initialize devices to an empty list
    try:
        # Scan for devices
        scanner = Scanner().withDelegate(ScanDelegate())
        log_info("Scanning for Bluetooth devices for 10 seconds...")
        # TODO: Make target device name configurable (e.g., via command-line argument or a constant)
        devices = scanner.scan(10.0)
        log_info("Scan complete.")
    except Exception as e:
        log_error(f"Bluetooth scanning failed: {e}")
        # Depending on the desired behavior, might exit or handle differently
        # For now, if scanning fails, 'devices' will be empty, and the script will report "iPhone not found".

    # Find your iPhone
    iphone_dev = None
    for dev in devices:
        log_info(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
        for (adtype, desc, value) in dev.getScanData():
            log_info(f"  {desc} = {value}")
        # TODO: Make target device name configurable (e.g., via command-line argument or a constant)
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
                log_info(f"Services discovered for {iphone_dev.addr}:")
                for service in services:
                    log_info(f"  Service UUID: {service.uuid}")
            except Exception as e:
                log_error(f"Error discovering services for {iphone_dev.addr}: {e}")
            finally:
                log_info(f"Disconnecting from {iphone_dev.addr}")
                peripheral.disconnect()
        else:
            log_warning(f"Failed to connect to iPhone ({iphone_dev.addr}) after multiple retries.")
    else:
        log_warning("iPhone not found during scan.")
