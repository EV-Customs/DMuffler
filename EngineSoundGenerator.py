    #!/usr/bin/env python3
"""
Create pitch varying audio of a library of cars in real-time on low processing power CPUs
"""

import os
import time
from logging_utils import log_info, log_warning
import simpleaudio as sa

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
            self.mc_laren_f1: 0,
            self.la_ferrari: 1,
            self.porcshe_911: 2,
            self.bmw_m4: 3,
            self.jaguar_e_type_series_1: 4,
            self.ford_model_t: 5,
            self.ford_mustang_gt350: 6
        }
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
        """
        if new_sound in self.engine_sounds_dict:
            self.engine_sound_id = self.engine_sounds_dict[new_sound]
            path_ending = os.path.join("./Sounds", new_sound)
            self.base_audio_filename = new_sound
            self.engine_sound_wave_object = sa.WaveObject.from_wave_file(path_ending)
            log_info(f"Engine sound changed to {new_sound}")
        else:
            log_warning(f"WARNING: New sound '{new_sound}' was NOT set. Keeping sound set to {self.base_audio_filename}")

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
        test1 = EngineSoundGenerator(EngineSoundGenerator.mc_laren_f1)
        assert test1.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1
        play_obj = test1.start_audio()
        time.sleep(1.5)
        test1.stop_audio(play_obj)

        test2 = EngineSoundGenerator("invalid_sound")
        assert test2.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1

        test3 = EngineSoundGenerator(EngineSoundGenerator.mc_laren_f1)
        assert test3.get_base_audio_filename() == EngineSoundGenerator.mc_laren_f1
        play_obj3 = test3.start_audio()
        time.sleep(1.5)
        test3.stop_audio(play_obj3)

        log_info("All EngineSoundGenerator unit tests passed.")

if __name__ == "__main__":
    EngineSoundGenerator.unit_test()
