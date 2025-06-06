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

## 3rd party libraries
try:
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
    print("Python can't find module in sys.path or requirements.txt or import statements above!")
    print("Please verify that .venvDMuffler virtual environment is running, if not run:")
    print("python3 -m venv .venvDMuffler")
    print("source .venvDMuffler/bin/activate")

## Internal libraries
import GlobalConstants as GC

class EngineSoundPitchShifter:

    # Global variables for keyboard input (to simulate gas pedal of a vehicle)
    isWPressed = False
    isEscPressed = False

    def __init__(self, baseAudioID: str):
        """ Constructor to initialize an EngineSoundPitchShifter object
            Defaults to McLaren F1 sound, if invalid baseAudio argumnet is passed

        Args:
            self: Newly created EngineSoundPitchShifter object
            baseAudioID (str): CONSTANT from GlobalConstants.py of audio file to be played and/or modulated

        Object instance variables:
            audioFilepath (str): Relative filepath of baseAudio audio clip
            audioTimeSeries (numpy.ndarray): Time series of audio data
            sampleRate (int): Sample rate of audio data
            playing (Bool): Flag to indicate if audio is currently playing
            currentFrame (int): Current frame of audio playback
            pitchFactor (float): Factor to modulate pitch of audio playback
            running (Bool): Flag to indicate if audio is currently running
            stream (Stream): Stream object for audio playback

        Returns:
            New EngineSoundPitchShifter() object
        """
        # Load audio file
        EngineSoundPitchShifterPyDirectory = os.path.dirname(os.path.abspath(__file__))
        self.audioFilepath = os.path.join(EngineSoundPitchShifterPyDirectory, GC.VEHICLE_ASSETS[int(baseAudioID)].sound)
        self.audioTimeSeries, self.sampleRate = librosa.load(self.audioFilepath)

        # Initialize playback variables
        self.playing = False
        self.currentFrame = 0
        self.pitchFactor = 1.0
        self.stream = None  # Initialize stream to None
        self.running = True # Assume running unless setup fails catastrophically

        # Setup audio stream using sounddevice library
        try:
            self.stream = sd.OutputStream(channels=1, samplerate=self.sampleRate, callback=self.audio_callback)
            self.stream.start()
            print("EngineSoundPitchShifter: Audio stream started.")
        except sd.PortAudioError as pae:
            # This error occurs if no audio device is found (common in CI/sandbox)
            print(f"EngineSoundPitchShifter: PortAudioError initializing stream (expected in some environments): {pae}")
            # self.stream remains None, playback will not be possible.
            # self.running can remain true, as other logic might not depend on the stream.
        except NameError: # This was the original except, for sd not being defined
            print("EngineSoundPitchShifter: Sounddevice object (sd) is not defined.")
            self.running = False # If sd is not defined, critical failure.
        except Exception as e:
            print(f"EngineSoundPitchShifter: An unexpected error occurred during audio stream setup: {e}")
            self.running = False # Unexpected error, probably critical.


    def cleanup(self):
        """ Stop the audio stream and release resources
        """
        if hasattr(self, 'stream') and self.stream is not None and self.stream.active:
            self.stream.stop()
            self.stream.close()
            print("EngineSoundPitchShifter: Audio stream stopped and closed.")
        else:
            print("EngineSoundPitchShifter: No active audio stream to cleanup or stream was not initialized.")
        self.running = False


    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(f"EngineSoundPitchShifter: Audio callback status: {status}")

        if self.playing and self.currentFrame < len(self.audioTimeSeries) and self.stream is not None:
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
            if key.char.upper() == 'W':
                isWPressed = True
                print(" key pressed, revving engine up")
        except AttributeError:
            # Special key
            pass


    def on_release(self, key):
        global isWPressed, isEscPressed

        try:
            if key.char.upper() == 'W':
                isWPressed = False
                print(" key released, engine revving down")

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

        while(True):
            self.simulate_gas_pedal()


if __name__ == "__main__":
    teslaModel3 = EngineSoundPitchShifter(GC.MC_LAREN_F1)
    teslaModel3.unit_test()
    teslaModel3.cleanup()
