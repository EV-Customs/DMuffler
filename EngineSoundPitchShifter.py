"""
__author__     = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "0.0.1"
__doc__        = "Create pitch varying audio in real-time on low processing power CPUs"
"""


## Standard Python libraries
import time            # https://docs.python.org/3/library/time.html
import threading       # https://docs.python.org/3/library/threading.html

## 3rd party libraries
try:
    # Peek makes printing debug information easy and adds basic benchmarking functionality (see https://salabim.org/peek)
    # pip install peek-python
    import peek

    # Audio analysis, with building blocks necessary to create music information retrieval systems
    # https://librosa.org/doc/latest/index.html
    import librosa

    # Play and record NumPy arrays containing audio signals.
    # https://python-sounddevice.readthedocs.io/
    import sounddevice as sd
    import numpy as np

    # Control and monitor input devices (mouse & keyboard)
    # https://pypi.org/project/pynput/
    from pynput import keyboard

except ImportError :
    peek("Please verify that .venvDMuffler virtual environment is running, if not run: ", color="red")
    peek("source .venvDMuffler/bin/activate", color="yellow")
    peek("pip install -r requirements.txt", color="yellow")
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

except ModuleNotFoundError:
    peek("Python can't find module in sys.path or there was a typo in requirements.txt or import statements above!", color="red")


class EngineSoundPitchShifter:
    # import EngineSoundPitchShifter as ESPS

    # Internal Combustion Enginer (ICE) car engine sound CONSTANTS
    MC_LAREN_F1 = "McLarenF1.wav"
    LA_FERRARI = "LaFerrari.wav"
    PORCSHE_911 = "Porcshe911.wav"
    BMW_M4 = "BMW_M4.wav"
    JAGUAR_E_TYPE_SERIES_1 = "JaguarEtypeSeries1.wav"
    FORD_MODEL_T = "FordModelT.wav"
    FORD_MUSTANG_GT350 = "FordMustangGT350.wav"

    def __init__(self, baseAudio):
        """ Constructor to initialize an EngineSoundPitchShifter object
            Defaults to McLaren F1 sound, if invalid baseAudio argumnet is passed

        Args:
            self: Newly created EngineSoundPitchShifter object
            baseAudio (str): CONSTANT filename of audio (.wav) file to be played and/or modulated

        Object instance variables:
            engineSoundsDict (dictionary): A 'Collection' of valid sounds and their IDs
            engineSoundID (int): Unique Sound ID to let embedded software communicate with mobile app
            selectedEngineSoundObject (simpleaudio object): Filepath defined audio clip

        Returns:
            New EngineSoundPitchShifter() object
        """

        # UPDATE this dictionary, EngineSoundPitchShifter.py CONSTANTS, and the DMuffler/Sounds folder to add new ICE sounds
        self.EngineSoundsDict = {
            EngineSoundPitchShifter.MC_LAREN_F1: 0,
            EngineSoundPitchShifter.LA_FERRARI: 1,
            EngineSoundPitchShifter.PORCSHE_911: 2,
            EngineSoundPitchShifter.BMW_M4: 3,
            EngineSoundPitchShifter.JAGUAR_E_TYPE_SERIES_1: 4,
            EngineSoundPitchShifter.FORD_MODEL_T: 5,
            EngineSoundPitchShifter.FORD_MUSTANG_GT350: 6
        }

    def on_keyboard_down_press(self, key):
        try:
            # Space bar controls playback
            if key == keyboard.Key.space:
                self.playing = not self.playing
                print(f"Playback: {'Playing' if self.playing else 'Paused'}")

            # Up arrow increases pitch
            elif key == keyboard.Key.up:
                self.pitch_factor = min(2.0, self.pitch_factor + 0.1)
                print(f"Pitch factor: {self.pitch_factor:.1f}")

            # Down arrow decreases pitch
            elif key == keyboard.Key.down:
                self.pitch_factor = max(0.5, self.pitch_factor - 0.1)
                print(f"Pitch factor: {self.pitch_factor:.1f}")

            # R key resets playback
            elif hasattr(key, 'char') and key.char.upper() == 'R':
                self.current_frame = 0
                print("Playback reset")

            # ESC key exits
            elif key == keyboard.Key.esc:
                self.running = False
                return False

        except AttributeError:
            pass


    def unit_test(self):
        while(True):
            #self.on_keyboard_down_press(keyboard.Key)

            self.on_keyboard_down_press(keyboard.KeyCode.from_char('up'))
            #self.on_keyboard_down_press(keyboard.Key.down)
            #self.on_keyboard_down_press(keyboard.Key.space)
            #self.on_keyboard_down_press(keyboard.Key.esc)
            #self.on_keyboard_down_press(keyboard.KeyCode.from_char('R'))
            time.sleep(1)

    def main(self):
        pass

if __name__ == "__main__":
    teslaModel3 = EngineSoundPitchShifter(EngineSoundPitchShifter.MC_LAREN_F1)
    teslaModel3.unit_test()
