#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "2025.0"
__doc__        = "Code entry point for DMuffler embedded application"
"""

# Disable PyLint linting messages
# https://pypi.org/project/pylint/
# pylint: disable=line-too-long
# pylint: disable=invalid-name

## Standard Python libraries
import time                         # https://docs.python.org/3/library/time.html
import argparse 		            # https://docs.python.org/3/library/argparse.html

## 3rd party libraries
#
#

# Peek makes printing debug information easy and adds basic benchmarking functionality (See https://salabim.org/peek)
# pip install peek-python
import peek

# Vehicle Identification Number (VIN) decoder that leverages the NHTSA API (See https://pypi.org/project/pyvin/)
# https://github.com/arpuffer/pyvin/blob/fa3ce109e7dd322ffd6ce64e1f523bb6fb432456/tests/vin_samples.py#L92
# pip install pyvin
from pyvin import VIN

## Internal libraries
#TODO from EngineSoundGenerator import *
## Internal libraries
from Database import Database
from EngineSoundPitchShifter import EngineSoundPitchShifter as ESPS
#TODO Fix broken wheel from BluetoothConnector import ScanDelegate

def integration_test():
    """
    https://en.wikipedia.org/wiki/Integration_testing

    """
    esps = ESPS(ESPS.MC_LAREN_F1)
    esps.unit_test()

    #bleConnection = ScanDelegate()
    #bleConnection.unit_test()

def main(db: Database):
    pass


def play_external_audio():
    """
    Play external audio using a subprocess.

    This function runs a dummy command using subprocess to simulate playing external audio.
    """
    subprocess.run(['echo', 'Playing external audio...'])


def demo_delay(delay_time):
    """
    Pause execution for a specified amount of time.

    Args:
        delay_time (float): The time in seconds to pause execution.
    """
    time.sleep(delay_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DMuffler application in DEV, TESTING, or PRODUCTION mode?")
    parser.add_argument('--mode', nargs='+',choices=['DEV', 'TESTING', 'PRODUCTION'],
                        help='Configure state of GC.DEBUG_STATEMENTS_ON and whether integration_test() or main() is called.')

    args = parser.parse_args()

    # Create/connect to a dev database
    devDB = Database("DMufflerLocalDev.db")

    # Create/connect to a production database
    db = Database("DMufflerDatabase.db") #TODO: Turo Online Database

    if 'DEV' in args.mode:
        peek.peek("DMuffler booting in DEV mode", color="red")
        firstName = input("Please enter first name to add new user: ")
        vin = input("Please enter VIN to add vehicle to an existing user: ") #https://vpic.nhtsa.dot.gov/api/
        color = input("Please enter the color (6 digit HEX code if possible) of vehicle: ")
        vehicle = VIN(vin.strip().upper())
        peek(f"Make: {vehicle.Make}, Model: {vehicle.Model}, Year: {vehicle.ModelYear}")



    elif 'TESTING' in args.mode:
        peek("DMuffler booting in TESTING mode", color="red")
        integration_test(devDB)


    elif 'PRODUCTION' in args.mode:
        peek("DMuffler booting in standard PRODUCTION mode", color="green")
        main(db)
