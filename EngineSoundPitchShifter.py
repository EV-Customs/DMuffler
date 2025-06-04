"""
__author__     = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "0.0.1" # Consider semantic versioning
__doc__        = "Creates pitch-varying engine audio in real-time using librosa for pitch shifting and sounddevice for playback. Responds to keyboard input for simulating gas pedal control."
"""

# Standard Python libraries
from time import sleep
import os
import sys

# Third-party libraries
try:
    import librosa
    import sounddevice as sd
    import numpy as np
    from pynput import keyboard
except ImportError as e:
    # logging_utils might not be available if this is the first import failure.
    # Using a print statement for this critical startup error.
    print(f"CRITICAL ERROR: Missing essential libraries: {e}. Please install librosa, sounddevice, numpy, and pynput.", file=sys.stderr)
    sys.exit(1)

# Local application/library specific imports
import GlobalConstants as GC
from logging_utils import log_error, log_info, log_warning

class EngineSoundPitchShifter:
    """
    Manages loading, pitch shifting, and real-time playback of an engine sound.
    Keyboard 'W' key simulates a gas pedal to control the pitch.
    """

    def __init__(self, base_audio_filename: str):
        """
        Constructor for EngineSoundPitchShifter.

        Args:
            base_audio_filename (str): Filename of the base audio (e.g., "mclaren_f1.wav")
                                       to be loaded from GC.SOUNDS_BASE_PATH.

        Instance Variables:
            audio_filepath (Path): Absolute path to the loaded audio file.
            audio_time_series (np.ndarray): Time series of audio data.
            sample_rate (int): Sample rate of the audio data.
            playing (bool): Flag to indicate if audio playback is active in the callback.
            current_frame (int): Current frame index for audio playback.
            pitch_factor (float): Factor to modulate the pitch of audio playback.
            running (bool): Flag to indicate if the audio stream is set up and processing is active.
            is_w_pressed (bool): State of the 'W' key (gas pedal simulation).
            stream (sd.OutputStream | None): sounddevice OutputStream object for audio playback.
        """
        self.audio_filepath = None
        self.audio_time_series = np.array([])
        self.sample_rate = 0

        self.playing = False # Controls if audio_callback outputs sound or silence
        self.current_frame = 0
        self.pitch_factor = 1.0
        self.is_w_pressed = False
        # self.is_esc_pressed is removed as it's unused.

        self.stream = None
        self.running = False # Indicates if the stream is successfully set up and running

        if not base_audio_filename:
            log_error("Initialization failed: No base audio filename provided.")
            return # self.running remains False

        try:
            # Construct absolute Path using GC.SOUNDS_BASE_PATH (which is already absolute)
            self.audio_filepath = GC.SOUNDS_BASE_PATH / base_audio_filename
            log_info(f"Attempting to load audio file: {self.audio_filepath}")
            # librosa.load requires a string path
            self.audio_time_series, self.sample_rate = librosa.load(str(self.audio_filepath), sr=None) # sr=None to preserve original sample rate
            log_info(f"Successfully loaded '{base_audio_filename}'. Sample rate: {self.sample_rate}, Duration: {len(self.audio_time_series)/self.sample_rate:.2f}s")
        except FileNotFoundError:
            log_error(f"Audio file not found at {self.audio_filepath}. EngineSoundPitchShifter will not run.")
            return # self.running remains False
        except Exception as e: # Catch other librosa load errors
            log_error(f"Error loading audio file {self.audio_filepath}: {e}. EngineSoundPitchShifter will not run.")
            return # self.running remains False

        try:
            log_info("Initializing audio stream...")
            self.stream = sd.OutputStream(
                channels=1, # Assuming mono audio for engine sounds
                samplerate=self.sample_rate,
                callback=self.audio_callback
            )
            self.stream.start()
            self.running = True # Stream successfully started
            self.playing = True # Start playing immediately after successful setup
            log_info("Audio stream started successfully.")
        except sd.PortAudioError as pae: # More specific exception for sounddevice issues
            log_error(f"PortAudio error initializing audio stream: {pae}. Soundevice may not be configured correctly.")
            self.stream = None # Ensure stream is None if it failed
        except Exception as e:
            log_error(f"Failed to initialize or start audio stream: {e}")
            self.stream = None # Ensure stream is None if it failed
        # If stream setup fails, self.running remains False

    def cleanup(self):
        """Stops the audio stream, releases resources, and stops keyboard listener if active."""
        log_info("Cleaning up EngineSoundPitchShifter resources...")
        if hasattr(self, 'stream') and self.stream: # Check if stream exists
            if self.stream.active:
                log_info("Stopping audio stream...")
                self.stream.stop()
            log_info("Closing audio stream...")
            self.stream.close()
        else:
            log_info("Audio stream was not active or already cleaned up.")

        self.running = False
        self.playing = False
        log_info("Cleanup complete.")

    def audio_callback(self, outdata: np.ndarray, frames: int, time, status):
        """
        Audio callback function called by sounddevice to provide audio data.

        Args:
            outdata (np.ndarray): Output buffer to fill with audio data.
                                  Shape is (frames, channels).
            frames (int): Number of frames to generate.
            time: Timing information (not typically used for simple playback).
            status: Stream status flags (e.g., for underflow/overflow).
        """
        if status:
            log_warning(f"Audio callback status: {status}")

        if self.playing and self.current_frame < len(self.audio_time_series):
            remaining_frames = len(self.audio_time_series) - self.current_frame
            chunk_size = min(frames, remaining_frames)

            chunk = self.audio_time_series[self.current_frame : self.current_frame + chunk_size]

            if chunk_size > 0:
                # Apply pitch shift using librosa.
                # n_steps: Number of semitones to shift. Positive values shift up, negative down.
                # 12 * np.log2(pitchFactor) converts a pitch factor (e.g., 2.0 for one octave up)
                # into the equivalent number of semitones.
                shifted_chunk = librosa.effects.pitch_shift(
                    y=chunk, # Renamed for clarity to match librosa docs
                    sr=self.sample_rate,
                    n_steps=12 * np.log2(self.pitch_factor)
                )

                # Ensure the output array is the right size (frames, 1 channel)
                # Pad if the shifted chunk is smaller than requested frames (e.g., if chunk_size < frames)
                if len(shifted_chunk) < frames:
                    # Pad with zeros at the end to fill the 'frames' requirement
                    padding_size = frames - len(shifted_chunk)
                    padded_shifted_chunk = np.pad(shifted_chunk, (0, padding_size), 'constant')
                else:
                    padded_shifted_chunk = shifted_chunk

                outdata[:] = padded_shifted_chunk.reshape(-1, 1)
                self.current_frame += chunk_size
            else: # Should not happen if remaining_frames > 0 and chunk_size calculated correctly
                outdata.fill(0)
        else: # Not playing or end of audio data
            outdata.fill(0)
            if self.playing and self.current_frame >= len(self.audio_time_series):
                # Optional: Loop audio by resetting current_frame, or stop playing
                # log_info("Audio reached end, looping...")
                # self.current_frame = 0
                # For now, it just plays silence once audio ends.
                self.playing = False # Stop playing after reaching the end
                log_info("Audio playback finished.")


    def on_press(self, key):
        """Handles key press events for controlling pitch."""
        try:
            if key.char.upper() == 'W':
                self.is_w_pressed = True
                log_info("Gas pedal (W key) pressed - increasing pitch.")
        except AttributeError:
            # Special keys (like Shift, Ctrl, etc.) don't have 'char' attribute
            if key == keyboard.Key.esc: # Example for future use if is_esc_pressed is re-added
                # self.is_esc_pressed = True
                # log_info("Escape key pressed.")
                pass


    def on_release(self, key):
        """Handles key release events for controlling pitch."""
        try:
            if key.char.upper() == 'W':
                self.is_w_pressed = False
                log_info("Gas pedal (W key) released - decreasing pitch.")
        except AttributeError:
            # Special keys
            if key == keyboard.Key.esc: # Example for future use if is_esc_pressed is re-added
                # self.is_esc_pressed = False
                pass

    def simulate_gas_pedal(self):
        """Simulates gas pedal behavior by adjusting pitch_factor based on W key state."""
        if self.is_w_pressed:
            # Gradually increase pitch while W is held, up to a maximum of 2.0
            self.pitch_factor = min(2.0, self.pitch_factor + 0.02)
        else:
            # Gradually return to normal pitch (1.0) when W is released
            if self.pitch_factor > 1.0:
                self.pitch_factor = max(1.0, self.pitch_factor - 0.02)
        # log_debug(f"Pitch factor: {self.pitch_factor:.2f}") # Optional: for fine-tuning

    def run_simulation_loop(self):
        """
        Main loop for running the pitch shifter simulation with keyboard control.
        This method includes the keyboard listener setup and the simulation ticks.
        """
        if not self.running:
            log_warning("Audio stream not running. Cannot start simulation loop.")
            return

        # Setup keyboard listener
        # The listener should run in a non-blocking way or this loop won't execute.
        # pynput.keyboard.Listener is typically run in its own thread.
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start() # Starts the listener thread
        log_info("Keyboard listener started. Press 'W' to simulate gas pedal. Press Ctrl+C in console to exit.")

        try:
            while self.running: # Loop controlled by self.running state
                self.simulate_gas_pedal()
                sleep(0.01)  # Main simulation tick rate (10ms delay)
        except KeyboardInterrupt:
            log_info("KeyboardInterrupt received. Shutting down simulation loop.")
        finally:
            if listener.is_alive():
                log_info("Stopping keyboard listener...")
                listener.stop()
                listener.join() # Wait for listener thread to finish
            log_info("Keyboard listener stopped.")
            self.cleanup() # Ensure cleanup is called when loop exits

if __name__ == "__main__":
    log_info("EngineSoundPitchShifter script started directly.")

    # Using a standardized filename constant from GlobalConstants
    # Ensure this file exists at GC.SOUNDS_BASE_PATH / GC.MCLAREN_F1_FILENAME
    pitch_shifter = EngineSoundPitchShifter(GC.MCLAREN_F1_FILENAME)

    if pitch_shifter.running:
        pitch_shifter.run_simulation_loop() # This method now contains the main loop logic
    else:
        log_error("EngineSoundPitchShifter did not initialize correctly. Cannot run simulation.")

    log_info("EngineSoundPitchShifter script finished.")
