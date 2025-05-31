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
# Removed global-statement as it's no longer needed after refactoring.

## Standard Python libraries
from time import sleep 
import os              
import logging # Using standard logging. Replace with logging_utils if available.

## 3rd party libraries
try:
    import librosa
    import sounddevice as sd
    import numpy as np
    from pynput import keyboard
except ImportError as e:
    # If logging_utils.log_error is the required function, it should be imported.
    # from logging_utils import log_error
    # log_error(f"Critical import error: {e}. Application dependencies missing.")
    logging.critical(f"Critical import error: {e}. Application dependencies missing.")
    raise # Re-raise the ImportError as per requirement

## Internal libraries
import GlobalConstants as GC
# from logging_utils import log_error # Placeholder for the import if it's a custom module

class EngineSoundPitchShifter:

    def __init__(self, baseAudioFilename):
        """ Constructor to initialize an EngineSoundPitchShifter object
            Defaults to McLaren F1 sound, if invalid baseAudio argumnet is passed
        """
        self.isWPressed = False     # Instance variable for 'W' key state
        self.isEscPressed = False   # Instance variable for 'Esc' key state

        self.running = False  # Default to not running; set to True upon successful stream init
        self.stream = None    # Initialize stream attribute
        self.playing = False
        self.currentFrame = 0
        self.pitchFactor = 1.0

        # Load audio file
        EngineSoundPitchShifterPyDirectory = os.path.dirname(os.path.abspath(__file__))
        self.audioFilepath = os.path.join(EngineSoundPitchShifterPyDirectory, "static", "sounds", baseAudioFilename)
        
        try:
            self.audioTimeSeries, self.sampleRate = librosa.load(self.audioFilepath)
        except Exception as e: # Catching generic exception for librosa.load as specific one isn't documented broadly
            # log_error(f"Error loading audio file {self.audioFilepath}: {e}")
            logging.error(f"Error loading audio file {self.audioFilepath}: {e}")
            # self.running remains False, __init__ should ideally indicate failure.
            return # Exit __init__ if audio loading fails, object will be partially formed.

        # Setup audio stream using sounddevice library
        try:
            # Ensure sd is available (it should be, due to the earlier try-except ImportError)
            self.stream = sd.OutputStream(
                channels=1, 
                samplerate=self.sampleRate, 
                callback=self.audio_callback
            )
            self.stream.start()
            self.running = True # Set to True only if stream is successfully created and started
            logging.info("Audio stream started successfully.")

        except sd.PortAudioError as pae: # Specific error for sounddevice issues
            # log_error(f"PortAudioError during audio stream setup: {pae}")
            logging.error(f"PortAudioError during audio stream setup: {pae}")
            # self.running remains False
        except Exception as e: # Catch other potential errors from sounddevice (e.g., configuration)
            # log_error(f"Failed to initialize or start audio stream: {e}")
            logging.error(f"Failed to initialize or start audio stream: {e}")
            # self.running remains False
        
        # If stream was created but failed to start, or any error occurred, and self.running is False
        # try to close the stream if it exists. This is a bit of cleanup within __init__.
        if not self.running and self.stream is not None:
            try:
                self.stream.close()
            except Exception as ce:
                # log_error(f"Error closing stream during __init__ cleanup after failure: {ce}")
                logging.error(f"Error closing stream during __init__ cleanup after failure: {ce}")


    def cleanup(self):
        """ Stop the audio stream and release resources """
        if hasattr(self, 'stream') and self.stream is not None and self.stream.active:
            try:
                self.stream.stop()
                self.stream.close()
                logging.info("Audio stream stopped and closed.")
            except Exception as e:
                # log_error(f"Error during stream cleanup: {e}")
                logging.error(f"Error during stream cleanup: {e}")
        self.running = False

    def audio_callback(self, outdata, frames, time, status):
        if status: # sounddevice specific status reporting
            # log_error(f"Audio callback status problem: {status}") # Assuming status indicates error
            logging.warning(f"Audio callback status: {status}") # Log non-critical status issues as warning

        if self.playing and self.currentFrame < len(self.audioTimeSeries):
            chunk = self.audioTimeSeries[self.currentFrame:self.currentFrame + frames]
            if len(chunk) > 0: # Ensure there is a chunk to process
                try:
                    shifted_chunk = librosa.effects.pitch_shift(
                        chunk,
                        sr=self.sampleRate, # Corrected from sr= to sr= for librosa v0.8+
                        n_steps=12 * np.log2(self.pitchFactor)
                    )
                    
                    # Ensure the output array is the right size (fill remaining with zeros if needed)
                    if len(shifted_chunk) < frames:
                        # Pad the shifted chunk if it's shorter than expected
                        processed_chunk = np.pad(shifted_chunk, (0, frames - len(shifted_chunk)))
                    else:
                        # Truncate if it's somehow longer (shouldn't happen with pitch_shift normally)
                        processed_chunk = shifted_chunk[:frames]
                    
                    outdata[:] = processed_chunk.reshape(-1, 1)
                    self.currentFrame += frames
                except Exception as e:
                    # log_error(f"Error during pitch shifting or audio processing in callback: {e}")
                    logging.error(f"Error during pitch shifting or audio processing in callback: {e}")
                    outdata.fill(0) # Fill with silence on error
            else:
                outdata.fill(0) # No chunk to process, fill with silence
        else:
            outdata.fill(0) # Not playing or end of audio, fill with silence

    def on_press(self, key):
        # No longer need global statements
        try:
            if key.char.upper() == 'W':
                self.isWPressed = True
                logging.debug("W key pressed, revving engine up.")
        except AttributeError:
            # Special key (e.g., Shift, Esc) was pressed
            if key == keyboard.Key.esc: # Example for handling Esc key if needed
                self.isEscPressed = True # This could be used to stop the simulation
                logging.debug("Escape key pressed.")
            pass

    def on_release(self, key):
        # No longer need global statements
        try:
            if key.char.upper() == 'W':
                self.isWPressed = False
                logging.debug("W key released.")
        except AttributeError:
            if key == keyboard.Key.esc: # Example for handling Esc key release
                # self.isEscPressed = False # If you want toggle behaviour, not currently used this way
                pass
            pass

    def simulate_gas_pedal(self):
        # Loop should ideally depend on self.running for clean exit
        while self.running: # Check self.running to allow external stop
            if self.isWPressed: # Accessing instance variable
                self.pitchFactor = min(2.0, self.pitchFactor + 0.02)
            else:
                if self.pitchFactor > 1.0:
                    self.pitchFactor = max(1.0, self.pitchFactor - 0.02)
            
            if self.isEscPressed: # Accessing instance variable
                logging.info("Escape pressed, stopping simulation.")
                self.running = False # Signal to stop all loops
                break 
            sleep(0.01)  # Small 10 ms delay to prevent excessive CPU usage

    def unit_test(self):
        """
        Listens for W and ESC key presses then calls simulate_gas_pedal()
        """
        if not self.running:
            logging.error("Audio stream not running. Aborting unit_test.")
            return

        # Setup keyboard listener
        # Making listener an instance variable if it needs to be accessed by other methods or for cleaner stop
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        logging.info("Keyboard listener started for unit_test. Press 'W' to simulate gas, 'Esc' to stop.")
        
        self.playing = True # Start audio playback for the test

        try:
            # simulate_gas_pedal will run while self.running is True.
            # self.isEscPressed is set by on_press and checked in simulate_gas_pedal to set self.running = False.
            self.simulate_gas_pedal() 

        except KeyboardInterrupt: # Allow manual stop with Ctrl+C
            logging.info("KeyboardInterrupt received, stopping unit_test.")
            self.running = False # Ensure running flag is set to false
        finally:
            self.playing = False # Stop audio playback
            if hasattr(self, 'listener'):
                self.listener.stop()
                logging.info("Keyboard listener stopped.")
            self.cleanup() # Ensure all resources are released

if __name__ == "__main__":
    # Setup basic logging for the main execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Determine the path to the static/sounds directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.join(script_dir, "static", "sounds")
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        logging.info(f"Created directory: {sounds_dir}")

    # Define a default audio file for testing if GlobalConstants doesn't provide one
    # or if the specified file doesn't exist.
    audio_filename_to_use = "mclaren_f1_placeholder.wav" # A placeholder name
    
    # Attempt to use MC_LAREN_F1 from GlobalConstants if available
    if hasattr(GC, 'MC_LAREN_F1') and GC.MC_LAREN_F1:
        audio_filename_to_use = GC.MC_LAREN_F1

    target_audio_filepath = os.path.join(sounds_dir, audio_filename_to_use)

    # Create a dummy WAV file if the target audio file does not exist.
    # This helps in making the script runnable for testing basic functionality
    # without needing the actual audio file immediately.
    if not os.path.exists(target_audio_filepath):
        logging.warning(f"Audio file {target_audio_filepath} not found. Creating a dummy WAV file.")
        try:
            # Attempt to import soundfile for creating a dummy WAV
            import soundfile as sf 
            samplerate = 44100
            duration = 1 # 1 second
            amplitude = 0.2 # Non-zero amplitude
            # Create a simple sine wave for the dummy audio
            frequency = 440 # A4 note
            t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
            data = amplitude * np.sin(2 * np.pi * frequency * t)
            data = data.astype(np.float32) # Ensure data is float32 for many audio interfaces
            
            sf.write(target_audio_filepath, data, samplerate, subtype='FLOAT')
            logging.info(f"Created dummy audio file: {target_audio_filepath}")
        except ImportError:
            logging.error("`soundfile` library is not installed. Cannot create dummy WAV file. Please install it (`pip install soundfile`).")
        except Exception as e:
            logging.error(f"Could not create dummy audio file {target_audio_filepath}: {e}")
            # If dummy file creation fails, the application might not run correctly.

    # Pre-check if sounddevice can operate, as a diagnostic step.
    try:
        sd.query_devices()
        logging.info(f"Sounddevice available. Default input: {sd.default.device[0]}, Default output: {sd.default.device[1]}")
    except Exception as e: 
        logging.critical(f"Sounddevice query failed or not properly configured: {e}. Audio functions may fail.")
        # Depending on how critical audio is, one might choose to exit.
        # For this script, we'll let it try to initialize EngineSoundPitchShifter.

    # Initialize and run the application
    teslaModel3 = EngineSoundPitchShifter(audio_filename_to_use) # Pass only filename, path is constructed inside
    
    if teslaModel3.running:
        logging.info("EngineSoundPitchShifter initialized successfully. Starting unit test...")
        teslaModel3.unit_test() # This now contains the main loop and cleanup
    else:
        logging.error("EngineSoundPitchShifter failed to initialize. Skipping unit test and cleaning up.")
        teslaModel3.cleanup() # Explicitly call cleanup if unit_test is not run due to init failure.
    
    logging.info("Application finished.")
