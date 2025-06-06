    #!/usr/bin/env python3
"""
Create pitch varying audio of a library of cars in real-time on low processing power CPUs
"""

import os
import time
from logging_utils import log_info, log_warning
import simpleaudio as sa
import GlobalConstants as GC

class EngineSoundGenerator:
    """
    Generates and plays engine sounds for a library of cars.
    """

    mc_laren_f1 = "mclaren_f1.wav"
    la_ferrari = "la_ferrari.wav"
    porcshe_911 = "porcshe_911.wav"
    bmw_m4 = "bmw_m4.wav"
    jaguar_e_type_series_1 = "jaguar_e_type_series_1.wav"
    ford_model_t = "ford_model_t.wav"
    ford_mustang_gt350 = "ford_mustang_gt350.wav"

    def __init__(self, base_audio):
        """
        Initialize the EngineSoundGenerator.

        Args:
            base_audio (str): The filename of the base audio to use.
        """
        self.engine_sounds_dict = {
            self.mc_laren_f1: GC.MC_LAREN_F1,
            self.la_ferrari: GC.LA_FERRARI,
            self.porcshe_911: GC.PORCSHE_911,
            self.bmw_m4: GC.BMW_M4,
            self.jaguar_e_type_series_1: GC.JAGUAR_E_TYPE_SERIES_1,
            self.ford_model_t: GC.FORD_MODEL_T,
            self.ford_mustang_gt350: GC.FORD_MUSTANG_GT350
        }
        # Initialize attributes to ensure they exist
        self.base_audio_filename = None
        self.engine_sound_wave_object = None
        self.engine_sound_id = None

        self.set_engine_sound(base_audio)

        # If the initial sound setting failed (e.g., base_audio was invalid or path not found)
        # and base_audio_filename wasn't successfully set, then set a default sound.
        # A successful set_engine_sound call should set self.engine_sound_wave_object.
        if not self.engine_sound_wave_object:
            log_warning(f"Initial sound '{base_audio}' failed to load or was invalid. Attempting to load default sound '{self.mc_laren_f1}'.")
            self.set_engine_sound(self.mc_laren_f1)

            # If default sound also failed, log a critical warning.
            if not self.engine_sound_wave_object:
                log_warning(f"CRITICAL: Default sound '{self.mc_laren_f1}' also failed to load. EngineSoundGenerator may not function correctly.")
                # self.base_audio_filename might be the default key, but no object loaded.
                # Or it might still be the original base_audio if that key was valid but path failed.

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
            # Ensure wave object exists before trying to play
            if not self.engine_sound_wave_object:
                log_warning("Cannot start audio loop: engine_sound_wave_object is not loaded.")
                return
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
        """
        if new_sound in self.engine_sounds_dict:
            target_engine_sound_id = self.engine_sounds_dict[new_sound]
            engine_sound_path = None
            for asset in GC.VEHICLE_ASSETS:
                if asset.engineSoundID == target_engine_sound_id:
                    engine_sound_path = asset.sound
                    break

            if engine_sound_path:
                # Attempt to load the new sound file
                try:
                    # Validate path existence before loading, simpleaudio might not give a clean error for Not Found
                    if not os.path.isfile(engine_sound_path):
                        log_warning(f"WARNING: Sound file not found at path '{engine_sound_path}' for key '{new_sound}'. Keeping current sound: {self.base_audio_filename}")
                        return # Keep current sound if file does not exist

                    wave_obj = sa.WaveObject.from_wave_file(engine_sound_path)
                    # If loading is successful, then update the state
                    self.engine_sound_wave_object = wave_obj
                    self.engine_sound_id = target_engine_sound_id
                    self.base_audio_filename = new_sound
                    log_info(f"Engine sound changed to {self.base_audio_filename} using path {engine_sound_path}")
                except Exception as e:
                    log_warning(f"WARNING: Could not load sound file '{engine_sound_path}' for key '{new_sound}'. Error: {e}. Keeping current sound: {self.base_audio_filename}")
            else:
                # This case means engine_sound_path was None
                current_sound_display = self.base_audio_filename if hasattr(self, 'base_audio_filename') and self.base_audio_filename else "current (or None if not initialized)"
                log_warning(f"WARNING: Sound path not found in GC.VEHICLE_ASSETS for '{new_sound}' (ID: {target_engine_sound_id}). Keeping {current_sound_display}")
        else:
            # This handles cases where new_sound is not a valid key in engine_sounds_dict
            current_sound_display = self.base_audio_filename if hasattr(self, 'base_audio_filename') and self.base_audio_filename else "current (or None if not initialized)"
            log_warning(f"WARNING: New sound key '{new_sound}' was NOT found in engine_sounds_dict. Keeping {current_sound_display}")

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
        log_info("STARTING EngineSoundGenerator.py Unit Test")

        # Test 1: Initialize with a valid sound
        log_info("Unit Test 1: Initialize with mc_laren_f1")
        test1 = EngineSoundGenerator(EngineSoundGenerator.mc_laren_f1)
        assert test1.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1, \
            f"Test 1 Failed: Expected {EngineSoundGenerator.mc_laren_f1}, Got {test1.get_base_audio_filename()}"
        assert test1.engine_sound_wave_object is not None, "Test 1 Failed: engine_sound_wave_object is None"
        try:
            play_obj1 = test1.start_audio()
            if play_obj1:
                time.sleep(0.05) # Shorter sleep
                test1.stop_audio(play_obj1)
        except Exception as e: # Catch a more general exception first to inspect its type
            if e.__class__.__name__ == "SimpleaudioError": # Check type by name if direct import is tricky
                log_warning(f"Test 1: Audio playback failed (as expected in some environments): {e}")
            else:
                log_warning(f"Test 1: An unexpected error occurred during audio playback attempt: {e.__class__.__name__} {e}")


        # Test 2: Initialize with an invalid sound key, should default to mc_laren_f1
        log_info("Unit Test 2: Initialize with 'invalid_sound'")
        test2 = EngineSoundGenerator("invalid_sound")
        assert test2.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1, \
            f"Test 2 Failed: Expected default {EngineSoundGenerator.mc_laren_f1}, Got {test2.get_base_audio_filename()}"
        assert test2.engine_sound_wave_object is not None, "Test 2 Failed: engine_sound_wave_object is None after defaulting"
        try:
            play_obj2 = test2.start_audio()
            if play_obj2:
                time.sleep(0.05)
                test2.stop_audio(play_obj2)
        except Exception as e:
            if e.__class__.__name__ == "SimpleaudioError":
                log_warning(f"Test 2: Audio playback failed (as expected in some environments): {e}")
            else:
                log_warning(f"Test 2: An unexpected error occurred during audio playback attempt: {e.__class__.__name__} {e}")

        # Test 3: Attempt to change to a sound whose .wav file is known to be missing (la_ferrari)
        # It should keep the original sound (mc_laren_f1)
        log_info("Unit Test 3: Attempt to change to la_ferrari (known missing .wav file)")
        test3 = EngineSoundGenerator(EngineSoundGenerator.mc_laren_f1) # Start with mc_laren_f1
        original_wave_object = test3.engine_sound_wave_object # Save for comparison

        test3.set_engine_sound(EngineSoundGenerator.la_ferrari) # Attempt to set la_ferrari

        assert test3.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1, \
            f"Test 3 Failed: Expected {EngineSoundGenerator.mc_laren_f1} (original) after trying to set missing la_ferrari, Got {test3.get_base_audio_filename()}"
        assert test3.engine_sound_wave_object is original_wave_object, \
            "Test 3 Failed: engine_sound_wave_object should not have changed after attempting to set a sound with a missing file."

        # Try to play the original sound to ensure it's still functional
        try:
            play_obj3 = test3.start_audio()
            if play_obj3:
                time.sleep(0.05)
                test3.stop_audio(play_obj3)
        except Exception as e:
            if e.__class__.__name__ == "SimpleaudioError":
                log_warning(f"Test 3: Audio playback of original sound failed (as expected in some environments): {e}")
            else:
                log_warning(f"Test 3: An unexpected error occurred during audio playback attempt of original sound: {e.__class__.__name__} {e}")

        # Test 4: Try to set an invalid sound key after valid initialization, should keep current sound
        log_info("Unit Test 4: Try to set 'invalid_sound' after valid init")
        test4 = EngineSoundGenerator(EngineSoundGenerator.bmw_m4) # Start with BMW M4
        current_sound_before_invalid_set = test4.get_base_audio_filename()
        test4.set_engine_sound("invalid_sound_again")
        assert test4.get_base_audio_filename() == current_sound_before_invalid_set, \
            f"Test 4 Failed: Expected {current_sound_before_invalid_set}, Got {test4.get_base_audio_filename()}"
        assert test4.engine_sound_wave_object is not None, "Test 4 Failed: engine_sound_wave_object is None after trying to set invalid sound"
        try:
            play_obj4 = test4.start_audio()
            if play_obj4:
                time.sleep(0.05)
                test4.stop_audio(play_obj4)
        except Exception as e:
            if e.__class__.__name__ == "SimpleaudioError":
                log_warning(f"Test 4: Audio playback failed (as expected in some environments): {e}")
            else:
                log_warning(f"Test 4: An unexpected error occurred during audio playback attempt: {e.__class__.__name__} {e}")


        log_info("All EngineSoundGenerator unit tests completed. Audio playback may be skipped in environments without audio hardware.")

if __name__ == "__main__":
    EngineSoundGenerator.unit_test()
