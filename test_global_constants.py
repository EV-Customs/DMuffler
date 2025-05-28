import unittest
from unittest.mock import patch
import os # Required for os.path

# Import the module to be tested (or specific functions/constants if preferred)
import GlobalConstants as GC

class TestGlobalConstants(unittest.TestCase):

    @patch('os.path.isfile')
    def test_validate_assets_runs_successfully_when_files_exist(self, mock_isfile):
        """
        Tests that validate_assets() completes without raising FileNotFoundError
        when os.path.isfile returns True for all assets.
        """
        mock_isfile.return_value = True # Simulate all files existing

        try:
            GC.validate_assets()
        except FileNotFoundError:
            self.fail("validate_assets() raised FileNotFoundError even when os.path.isfile returned True.")
        
        # Check that os.path.isfile was called for each asset path.
        # Each CarAsset has an 'image' and a 'sound' attribute.
        if GC.CAR_ASSETS: # Only assert call count if CAR_ASSETS is not empty
            expected_calls = len(GC.CAR_ASSETS) * 2
            self.assertEqual(mock_isfile.call_count, expected_calls,
                             f"Expected os.path.isfile to be called {expected_calls} times, but was called {mock_isfile.call_count} times.")
        else:
            self.assertEqual(mock_isfile.call_count, 0, "os.path.isfile should not be called if CAR_ASSETS is empty.")


    @patch('os.path.isfile')
    def test_validate_assets_raises_error_when_file_missing(self, mock_isfile):
        """
        Tests that validate_assets() raises FileNotFoundError
        when os.path.isfile returns False for at least one asset.
        """
        if not GC.CAR_ASSETS: # Handle case where CAR_ASSETS might be empty
            self.skipTest("CAR_ASSETS is empty, skipping test_validate_assets_raises_error_when_file_missing.")

        # Make os.path.isfile return False for the very first asset's image path
        # and True for all subsequent calls.
        # This ensures that the error is indeed raised when a file is "missing".
        
        # Store the original path of the first asset's image for assertion messages
        first_asset_image_path = GC.CAR_ASSETS[0].image
        
        def side_effect_isfile(path_arg):
            # This function will be called by os.path.isfile
            # If the path_arg matches the first asset's image path, return False. Otherwise, True.
            if path_arg == first_asset_image_path:
                return False # Simulate this specific file is missing
            return True # All other files exist

        mock_isfile.side_effect = side_effect_isfile

        with self.assertRaises(FileNotFoundError) as context:
            GC.validate_assets()
        
        # Assert that the error message contains the path of the (simulated) missing file
        self.assertIn(first_asset_image_path, str(context.exception),
                      "The FileNotFoundError message should contain the path of the missing file.")
        
        # The current validate_assets() implementation collects all missing files,
        # so it will iterate through all assets even if one is found missing early.
        expected_calls = len(GC.CAR_ASSETS) * 2
        self.assertEqual(mock_isfile.call_count, expected_calls,
                         "Expected os.path.isfile to be called for all assets.")

    def test_car_assets_paths_use_os_path_join(self):
        """
        Tests that all paths in CAR_ASSETS are constructed using os.path.join.
        This is more of a convention check. It assumes that if a path contains
        os.sep, it was likely joined. This is not a perfect test for os.path.join
        usage but a reasonable heuristic.
        """
        if not GC.CAR_ASSETS:
            self.skipTest("CAR_ASSETS is empty, skipping path join test.")
            
        for asset in GC.CAR_ASSETS:
            self.assertIn(os.sep, asset.image, f"Image path for {asset.name} does not seem to use os.path.join: {asset.image}")
            self.assertIn(os.sep, asset.sound, f"Sound path for {asset.name} does not seem to use os.path.join: {asset.sound}")

    def test_sound_file_extensions_are_wav(self):
        """
        Tests that all sound files in CAR_ASSETS and EngineSoundsDict related constants use .wav extension.
        """
        if not GC.CAR_ASSETS:
            self.skipTest("CAR_ASSETS is empty, skipping .wav extension test.")

        for asset in GC.CAR_ASSETS:
            self.assertTrue(asset.sound.endswith(".wav"), f"Sound path for {asset.name} should end with .wav: {asset.sound}")
        
        # Check constants used in EngineSoundsDict
        for sound_const_name, sound_id in GC.EngineSoundsDict.items():
            # Assuming the keys of EngineSoundsDict are the actual filenames (which they are after recent refactoring)
            # Or, if they are variable names, then getattr(GC, sound_const_name)
            # Based on recent refactoring, keys are variables like GC.MC_LAREN_F1 which hold the filename string.
             self.assertTrue(sound_const_name.endswith(".wav"), f"Sound constant value {sound_const_name} for ID {sound_id} should end with .wav")


if __name__ == '__main__':
    unittest.main()
