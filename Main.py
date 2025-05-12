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

## Standard Python libraries
import argparse 		            # https://docs.python.org/3/library/argparse.html

## 3rd party libraries
# Peek makes printing debug information easy and adds basic benchmarking functionality (see https://salabim.org/peek)
# pip install peek-python
import peek

## Internal libraries
#TODO from EngineSoundGenerator import *


def integration_test():
    """
    https://en.wikipedia.org/wiki/Integration_testing

    """
    pass


def main():
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

    if 'DEV' in args.mode:
        peek("DMuffler booting in DEV mode", color="red")
        peek("Install SQLite system wide on Raspberry Pi Compute Module 4 using:", color="yellow")
        peek("sudo apt install sqlite3", color="white")

    elif 'TESTING' in args.mode:
        peek("DMuffler booting in TESTING mode", color="red")
        integration_test()

    elif 'PRODUCTION' in args.mode:
        peek("DMuffler booting in standard PRODUCTION mode", color="green")
        main()
