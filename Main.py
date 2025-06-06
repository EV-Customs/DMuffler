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
import GlobalConstants as GC
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
from EngineSoundGenerator import EngineSoundGenerator
## Internal libraries
from Database import Database
from EngineSoundPitchShifter import EngineSoundPitchShifter as ESPS
#TODO Fix broken wheel from BluetoothConnector import ScanDelegate

def integration_test():
    """
    https://en.wikipedia.org/wiki/Integration_testing

    """
    esps = ESPS(GC.MC_LAREN_F1)
    # esps.unit_test() # Commented out due to NameError: name 'keyboard' is not defined and infinite loop

    print("Testing EngineSoundGenerator...")
    # mc_laren_f1 is "mclaren_f1.wav", which EngineSoundGenerator expects as a key.
    esg = EngineSoundGenerator(EngineSoundGenerator.mc_laren_f1)
    assert esg.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1
    try:
        play_obj = esg.start_audio()
        if play_obj:
            # A short delay is needed for the audio to actually play a bit.
            # time.sleep is already imported in Main.py
            time.sleep(0.1)
            esg.stop_audio(play_obj)
            print("EngineSoundGenerator playback test snippet executed.")
        else:
            # This case might occur if the default sound file itself is missing
            # and __init__ couldn't load engine_sound_wave_object.
            print("EngineSoundGenerator play_obj was None (sound might not have loaded).")
    except Exception as e:
        # Catch SimpleaudioError specifically if possible, or general Exception
        if e.__class__.__name__ == "SimpleaudioError":
            print(f"EngineSoundGenerator playback failed (expected in some environments): {e}")
        else:
            print(f"EngineSoundGenerator: An unexpected error occurred during playback attempt: {e}")

    #bleConnection = ScanDelegate()
    #bleConnection.unit_test()

def main(db: Database):
    pass


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
        # GC.validate_assets() # Original temporary placement idea
        firstName = input("Please enter first name to add new user: ")
        vin = input("Please enter VIN to add vehicle to an existing user: ") #https://vpic.nhtsa.dot.gov/api/
        color = input("Please enter the color (6 digit HEX code if possible) of vehicle: ")
        vehicle = VIN(vin.strip().upper())
        peek(f"Make: {vehicle.Make}, Model: {vehicle.Model}, Year: {vehicle.ModelYear}")



    elif 'TESTING' in args.mode:
        peek("DMuffler booting in TESTING mode", color="red")
        integration_test()


    elif 'PRODUCTION' in args.mode:
        peek("DMuffler booting in standard PRODUCTION mode", color="green")
        main(db)
