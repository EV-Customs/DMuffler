    #!/usr/bin/env python3
"""
Create pitch varying audio of a library of cars in real-time on low processing power CPUs
"""

import os
import time
from logging_utils import log_info, log_warning, log_error
import simpleaudio as sa
import GlobalConstants as GC # Added module-level import

class EngineSoundGenerator:
    """
    Generates and plays engine sounds for a library of cars.
    """

    # Sound filename constants are now centralized in GlobalConstants.py
    # The engine_sounds_dict is also centralized in GlobalConstants.EngineSoundsDict

    def __init__(self, base_audio):
        """
        Initialize the EngineSoundGenerator.

        Args:
            base_audio (str): The filename of the base audio to use. 
                              Should be one of the keys in GlobalConstants.EngineSoundsDict.
        """
        self.base_audio_filename = None
        self.engine_sound_wave_object = None
        self.engine_sound_id = -1

        # self.engine_sounds_dict is no longer defined here.
        # We will use GlobalConstants.EngineSoundsDict directly.
        self.set_engine_sound(base_audio)

    def start_audio(self):
        """
        Play sound once and return the play object.
        """
        play_obj = self.engine_sound_wave_object.play()
        return play_obj

    def start_audio_loop(self):
        """
        Play sound in loop forever (blocking).
        """
        while True:
            play_obj = self.engine_sound_wave_object.play()
            play_obj.wait_done()

    def stop_audio(self, play_obj):
        """
        Stop sound playing in last wait_done() function call.

        Args:
            play_obj: The play object.
        """
        play_obj.stop()

    def set_engine_sound(self, new_sound):
        """
        Change sound configured to play during the next start_audio_loop() function call.

        Args:
            new_sound (str): The filename of the new sound to use. 
                              Should be one of the keys in GlobalConstants.EngineSoundsDict.
        """
        if new_sound in GC.EngineSoundsDict: # Use GlobalConstants.EngineSoundsDict
            # Path construction logic remains the same.
            # Consider making the base path ("static/sounds") a global constant as well if used in multiple places.
            path_to_sound_file = os.path.join("static", "sounds", new_sound)

            try:
                wave_object = sa.WaveObject.from_wave_file(path_to_sound_file)
                # If loading is successful, then update instance variables
                self.engine_sound_id = GC.EngineSoundsDict[new_sound] # Get ID from GlobalConstants
                self.base_audio_filename = new_sound
                self.engine_sound_wave_object = wave_object
                log_info(f"Engine sound changed to {new_sound} from {path_to_sound_file}")
            except FileNotFoundError:
                log_error(f"ERROR: Audio file not found at {path_to_sound_file}. Sound not changed. Current sound: {self.base_audio_filename}")
            except Exception as e: # Catch other simpleaudio errors or invalid file format errors
                log_error(f"ERROR: Could not load audio file {path_to_sound_file}: {e}. Sound not changed. Current sound: {self.base_audio_filename}")
        else:
            log_warning(f"WARNING: Sound name '{new_sound}' is not a recognized engine sound (not found in GlobalConstants.EngineSoundsDict). Keeping sound set to {self.base_audio_filename}")

    def get_base_audio_filename(self):
        """
        Return the filename of the engine sound set to play.
        """
        return self.base_audio_filename

    @staticmethod
    def unit_test():
        """
        Run the unit test for the EngineSoundGenerator.
        """
        # Import GlobalConstants here for access to sound filenames
        import GlobalConstants as GC

        log_info("STARTING EngineSoundGenerator.py Unit Test")
        # Ensure that the sound file used for testing (e.g., GC.MC_LAREN_F1) actually exists
        # at the expected path static/sounds/mc_laren_f1.wav for the test to pass loading.
        # This might require creating a dummy file in test setup if not present.
        # For now, assuming it might exist or the test primarily checks logic.

        test1 = EngineSoundGenerator(GC.MC_LAREN_F1) # Use constant from GlobalConstants
        assert test1.get_base_audio_filename() == GC.MC_LAREN_F1
        
        # Check if wave object was loaded, otherwise start_audio will fail
        if test1.engine_sound_wave_object:
            play_obj = test1.start_audio()
            time.sleep(0.1) # Reduced sleep time for faster tests
            test1.stop_audio(play_obj)
        else:
            log_warning(f"Skipping audio playback in test1 as sound file {GC.MC_LAREN_F1} likely not loaded.")


        log_info("Testing with an invalid sound name ('invalid_sound')...")
        test2 = EngineSoundGenerator("invalid_sound")
        # Because "invalid_sound" is not in GlobalConstants.EngineSoundsDict,
        # set_engine_sound will log a warning.
        # self.base_audio_filename should remain None.
        # self.engine_sound_wave_object should remain None.
        # self.engine_sound_id should remain -1.
        assert test2.get_base_audio_filename() is None, \
            f"Expected base_audio_filename to be None, but got {test2.get_base_audio_filename()}"
        assert test2.engine_sound_wave_object is None, \
            f"Expected engine_sound_wave_object to be None, but got {type(test2.engine_sound_wave_object)}"
        assert test2.engine_sound_id == -1, \
            f"Expected engine_sound_id to be -1, but got {test2.engine_sound_id}"
        log_info("Test with invalid sound name passed.")

        # Test setting a valid sound after an invalid attempt (test2 instance)
        log_info("Testing setting a valid sound (GC.MC_LAREN_F1) on test2 instance...")
        test2.set_engine_sound(GC.MC_LAREN_F1) # Use constant from GlobalConstants
        assert test2.get_base_audio_filename() == GC.MC_LAREN_F1, \
            f"Expected base_audio_filename to be {GC.MC_LAREN_F1}, but got {test2.get_base_audio_filename()}"
        assert test2.engine_sound_wave_object is not None, "Expected engine_sound_wave_object to be not None if sound loaded"
        assert test2.engine_sound_id == GC.EngineSoundsDict[GC.MC_LAREN_F1], \
            f"Expected engine_sound_id to be {GC.EngineSoundsDict[GC.MC_LAREN_F1]}, but got {test2.engine_sound_id}"
        log_info("Test setting a valid sound on test2 instance passed.")


        log_info("Testing another valid sound instance (test3 with GC.PORSCHE_911)...")
        # Using PORSCHE_911 here for variety, assuming it's defined in GC and file exists
        test_sound_porsche = GC.PORSCHE_911 # From GlobalConstants, correctly spelled
        test3 = EngineSoundGenerator(test_sound_porsche) 
        assert test3.get_base_audio_filename() == test_sound_porsche
        if test3.engine_sound_wave_object:
            play_obj3 = test3.start_audio()
            time.sleep(0.1) # Reduced sleep time
            test3.stop_audio(play_obj3)
        else:
            log_warning(f"Skipping audio playback in test3 as sound file {test_sound_porsche} likely not loaded.")


        log_info("All EngineSoundGenerator unit tests passed (or skipped parts if files missing).")

if __name__ == "__main__":
    # It's good practice to ensure dummy files for testing exist if tests depend on them.
    # This __main__ block in the source file is for running its own unit tests.
    # For robust testing, test files should handle their own dummy file creation or mocking.
    # For now, we assume that if sound files are missing, tests log warnings and continue.
    
    # Import GlobalConstants for the main execution of unit_test
    import GlobalConstants as GC # Ensure GC is available in this scope if not already
    
    # Create dummy sound files if they don't exist to make unit tests more robust
    # This is a simplified version; ideally, test setup creates these in a test-specific directory.
    sounds_dir = os.path.join("static", "sounds")
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        log_info(f"Created directory for dummy sounds: {sounds_dir}")

    dummy_sound_files_to_check = [GC.MC_LAREN_F1, GC.PORSCHE_911] # Add others if used in tests
    for sound_file in dummy_sound_files_to_check:
        file_path = os.path.join(sounds_dir, sound_file)
        if not os.path.exists(file_path):
            try:
                # Create a minimal valid WAV file for testing simpleaudio.WaveObject.from_wave_file
                # This requires 'soundfile' library, or use a pre-existing dummy wav.
                import soundfile as sf
                import numpy as np
                samplerate = 44100; duration = 0.1; amplitude = 0.1
                data = amplitude * np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(samplerate*duration), endpoint=False))
                data = data.astype(np.float32)
                sf.write(file_path, data, samplerate, subtype='FLOAT')
                log_info(f"Created dummy WAV file: {file_path}")
            except ImportError:
                log_warning(f"Cannot create dummy WAV {file_path}: soundfile library not installed. Tests requiring this file might fail to load audio.")
            except Exception as e:
                log_error(f"Could not create dummy WAV file {file_path}: {e}")
    
    EngineSoundGenerator.unit_test()
