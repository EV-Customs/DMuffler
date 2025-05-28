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
import argparse                     # https://docs.python.org/3/library/argparse.html

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
from Database import Database
from EngineSoundPitchShifter import EngineSoundPitchShifter as ESPS
from GlobalConstants import validate_assets, MC_LAREN_F1 # Added MC_LAREN_F1 for ESPS example
from EngineSoundGenerator import EngineSoundGenerator 

def integration_test(db: Database): # Modified signature
    """
    Placeholder for integration tests.
    https://en.wikipedia.org/wiki/Integration_testing
    """
    peek.peek(f"Integration test function called with database: {db.db_path}", color="blue")
    # TODO: Implement actual integration tests that check interactions between components.
    # For example:
    # 1. Create EngineSoundGenerator, set a sound (e.g., EngineSoundGenerator.PORSCHE_911).
    #    sound_generator = EngineSoundGenerator(EngineSoundGenerator.PORSCHE_911) # Assuming PORSCHE_911 is defined
    # 2. Create EngineSoundPitchShifter with that sound.
    #    If EngineSoundGenerator provides the audio file path or data:
    #    pitch_shifter = ESPS(sound_generator.get_base_audio_filename()) # or similar
    #    (Note: ESPS constructor might need a filename like MC_LAREN_F1 from GlobalConstants)
    #    For a placeholder:
    #    peek.peek("Simulating EngineSoundGenerator and ESPS interaction.", color="cyan")
    #    try:
    #        esps_instance = ESPS(MC_LAREN_F1) # Using an existing constant for now
    #        peek.peek(f"ESPS instance created with {MC_LAREN_F1}", color="cyan")
    #        # Simulate some operations if possible, or just check instantiation.
    #    except Exception as e:
    #        peek.peek(f"Error during placeholder ESPS instantiation in integration_test: {e}", color="red")
    # 3. Simulate input to change pitch (conceptual).
    # 4. (Future) Verify audio output if possible.
    pass

def main(db: Database):
    # TODO: Implement main application logic using the database connection 'db'
    peek.peek(f"Main application function called with database: {db.db_path}", color="green") # Example use of db
    pass

# play_external_audio() function was removed in a previous refactoring step.

def demo_delay(delay_time):
    """
    Pause execution for a specified amount of time.

    Args:
        delay_time (float): The time in seconds to pause execution.
    """
    time.sleep(delay_time)


if __name__ == "__main__":
    try:
        validate_assets()
        peek.peek("Asset validation successful.", color="green")
    except FileNotFoundError as e:
        peek.peek(f"Asset validation failed: {e}", color="red")
        # Depending on desired behavior, might exit here:
        # import sys
        # sys.exit(1)

    parser = argparse.ArgumentParser(description="Run DMuffler application in DEV, TESTING, or PRODUCTION mode?")
    parser.add_argument('--mode', nargs='+',choices=['DEV', 'TESTING', 'PRODUCTION'],
                        help='Configure state of GC.DEBUG_STATEMENTS_ON and whether integration_test() or main() is called.',
                        required=True)

    args = parser.parse_args()

    # Create/connect to a dev database
    dev_db = Database("DMufflerLocalDev.db") # Renamed devDB to dev_db

    # Create/connect to a production database
    db = Database("DMufflerDatabase.db") #TODO: Turo Online Database

    if 'DEV' in args.mode:
        peek.peek("DMuffler booting in DEV mode", color="red")
        first_name = input("Please enter first name to add new user: ") # Renamed firstName to first_name
        vin_input = input("Please enter VIN to add vehicle to an existing user: ") #https://vpic.nhtsa.dot.gov/api/
        color = input("Please enter the color (6 digit HEX code if possible) of vehicle: ")
        try:
            vehicle = VIN(vin_input.strip().upper())
            # Attempt to access attributes to trigger potential errors if VIN is invalid
            peek.peek(f"Make: {vehicle.Make}, Model: {vehicle.Model}, Year: {vehicle.ModelYear}", color="yellow")
        except Exception as e: # Catching a general exception from pyvin or AttributeError
            peek.peek(f"Could not retrieve VIN details for '{vin_input}': {e}", color="red")
            # TODO: Consider how to handle this error in terms of user experience or next steps.

    elif 'TESTING' in args.mode:
        peek("DMuffler booting in TESTING mode", color="red")
        integration_test(dev_db) # Pass dev_db


    elif 'PRODUCTION' in args.mode:
        peek("DMuffler booting in standard PRODUCTION mode", color="green")
        main(db)
