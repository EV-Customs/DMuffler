"""
__author__     = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "0.0.1"
__doc__        = "Create pitch varying audio in real-time on low processing power CPUs"
"""

# Disable PyLint linting messages that seem unuseful
# https://pypi.org/project/pylint/
# pylint: disable=invalid-name
# pylint: disable=global-statement

## Standard Python libraries
from time import sleep # https://docs.python.org/3/library/time.html
import os              # https://docs.python.org/3/library/os.html
import threading       # https://docs.python.org/3/library/threading.html
from logging_utils import log_info, log_warning, log_error

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
    # import pyautogui or import keyboard

except ImportError :
    log_error("Python can't find module in sys.path or there may be a typo in requirements.txt or import statements above!")
    log_info("Please verify that .venvDMuffler virtual environment is running, if not run:")
    log_info("python3 -m venv .venvDMuffler")
    log_info("source .venvDMuffler/bin/activate")
    log_info("pip install -r requirements.txt")


class EngineSoundPitchShifter:
    # import EngineSoundPitchShifter as ESPS

    # Internal Combustion Enginer (ICE) car engine sound CONSTANTS
    MC_LAREN_F1 = "mclaren_f1.wav"
    LA_FERRARI = "LaFerrari.wav"
    PORCSHE_911 = "Porcshe911.wav"
    BMW_M4 = "BMW_M4.wav"
    JAGUAR_E_TYPE_SERIES_1 = "JaguarEtypeSeries1.wav"
    FORD_MODEL_T = "FordModelT.wav"
    FORD_MUSTANG_GT350 = "FordMustangGT350.wav"

    # Global variables for keyboard input (to simulate gas pedal of a vehicle)
    isWPressed = False
    isEscPressed = False

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

        # Load audio file
        self.audioFilename = baseAudio
        EngineSoundPitchShifterPyDirectory = os.path.dirname(os.path.abspath(__file__))
        soundPath = os.path.join(EngineSoundPitchShifterPyDirectory, "static", "sounds", self.audioFilename)
        self.audioTimeSeries, self.sampleRate = librosa.load(soundPath)

        # Initialize playback variables
        self.playing = False
        self.currentFrame = 0
        self.pitchFactor = 1.0
        self.running = True

        # Setup audio stream using sounddevice library
        try:
            self.stream = sd.OutputStream(channels=1, samplerate=self.sampleRate, callback=self.audio_callback)
        except NameError:
            # Handle the case where sd is not defined
            log_error("Sounddevice object is not defined")


        # Start the stream
        self.stream.start()


    def cleanup(self):
        """Stop the audio stream and release resources"""
        if hasattr(self, 'stream') and self.stream.active:
            self.stream.stop()
            self.stream.close()
        self.running = False


    def audio_callback(self, outdata, frames, time, status):
        if self.playing and self.currentFrame < len(self.audioTimeSeries):
            # Get chunk of audio
            chunk = self.audioTimeSeries[self.currentFrame:self.currentFrame + frames]

            # Apply pitch shift
            if len(chunk) > 0:
                shifted = librosa.effects.pitch_shift(
                    chunk,
                    sr=self.sampleRate,
                    n_steps=12 * np.log2(self.pitchFactor)
                )

                # Ensure the output array is the right size
                if len(shifted) < frames:
                    shifted = np.pad(shifted, (0, frames - len(shifted)))

                outdata[:] = shifted.reshape(-1, 1)
                self.currentFrame += frames
            else:
                outdata.fill(0)
        else:
            outdata.fill(0)


    def on_press(self, key):
        global isWPressed, isEscPressed

        try:
            if key.char == 'w':
                isWPressed = True
                log_info("W key pressed, revving engine up")
        except AttributeError:
            # Special key
            pass


    def on_release(self, key):
        global isWPressed, isEscPressed

        try:
            if key.char == 'w':
                isWPressed = False
                log_info("W key released, engine RPM's reducing")

        except AttributeError:
            # Special key
            pass

    def simulate_gas_pedal(self):
        global isWPressed, isEscPressed

        while self.running:
            # Simulate gas pedal with W key
            if self.isWPressed:
                # Gradually increase pitch while W is held
                self.pitchFactor = min(2.0, self.pitchFactor + 0.02)
            else:
                # Gradually return to normal pitch when W is released
                if self.pitchFactor > 1.0:
                    self.pitchFactor = max(1.0, self.pitchFactor - 0.02)

            sleep(0.01)  # Small 10 ms delay to prevent excessive CPU usage


    def unit_test(self):
        """
        """
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

        log_info("Keyboard Controls:")
        log_info("Space: Play/Pause")
        log_info("Up/Down arrows: Adjust pitch")
        log_info("R: Reset playback")
        log_info("W: Gas pedal (hold to increase pitch)")
        log_info("ESC: Exit program")

        while(True):
            self.simulate_gas_pedal()


if __name__ == "__main__":
    teslaModel3 = EngineSoundPitchShifter(EngineSoundPitchShifter.MC_LAREN_F1)
    log_info(f"Loaded audio file: {teslaModel3.audioFilename}")
    teslaModel3.unit_test()
    teslaModel3.cleanup()
