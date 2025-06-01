import unittest
from unittest.mock import patch, MagicMock, call
import sys
import argparse

if 'Main' in sys.modules:
    del sys.modules['Main']
if 'peek' in sys.modules:
    sys.modules['peek'] = MagicMock()

import Main as MainModule
from Database import Database
from EngineSoundPitchShifter import EngineSoundPitchShifter
import GlobalConstants as GC

# Ensure these are mocked *before* MainModule or EngineSoundPitchShifter might use them.
# This is done when the test file is first parsed.
mock_pynput_global = MagicMock()
mock_pynput_global.keyboard.Listener = MagicMock() # Mock the Listener class
sys.modules['pynput'] = mock_pynput_global
sys.modules['pynput.keyboard'] = mock_pynput_global.keyboard # Ensure pynput.keyboard is also the mock

mock_sd_module_global = MagicMock()
mock_sd_module_global.OutputStream = MagicMock()
sys.modules['sounddevice'] = mock_sd_module_global


class TestMainExecution(unittest.TestCase):

    def setUp(self):
        if 'Main' in sys.modules: # Refers to MainModule or MainExecutable
            del sys.modules['Main']

        self.mock_peek_function_for_assertions = MagicMock()
        mock_module_to_be_imported_as_peek = MagicMock()
        mock_module_to_be_imported_as_peek.peek = self.mock_peek_function_for_assertions

        self.peek_patcher = patch.dict(sys.modules, {'peek': mock_module_to_be_imported_as_peek})
        self.peek_patcher.start()

    def tearDown(self):
        self.peek_patcher.stop()
        if 'Main' in sys.modules:
            del sys.modules['Main']
        if 'MainExecutable' in sys.modules:
            del sys.modules['MainExecutable']

    @patch('argparse.ArgumentParser.parse_args')
    @patch('builtins.input')
    @patch('Main.VIN')
    @patch('Main.Database')
    def test_dev_mode(self, mock_database_constructor, mock_vin_class, mock_input, mock_parse_args):
        mock_parse_args.return_value = argparse.Namespace(mode=['DEV'])
        mock_input.side_effect = ['TestUser', 'TESTVIN123', 'Blue']
        mock_vehicle_instance = MagicMock(); mock_vehicle_instance.Make = "TestMake"; mock_vehicle_instance.Model = "TestModel"; mock_vehicle_instance.ModelYear = "2023"
        mock_vin_class.return_value = mock_vehicle_instance
        mock_dev_db_instance = MagicMock(spec=Database); mock_prod_db_instance = MagicMock(spec=Database)
        mock_database_constructor.side_effect = [mock_dev_db_instance, mock_prod_db_instance]

        original_argv = sys.argv
        sys.argv = ['Main.py', '--mode', 'DEV']

        if 'Main' in sys.modules: del sys.modules['Main']
        import Main as MainExecutable
        MainExecutable.Database = mock_database_constructor
        MainExecutable.VIN = mock_vin_class
        MainExecutable.peek = sys.modules['peek'] # Explicitly use the mocked peek
        sys.argv = original_argv

        self.mock_peek_function_for_assertions.assert_any_call("DMuffler booting in DEV mode", color="red")
        mock_input.assert_has_calls([
            call("Please enter first name to add new user: "),
            call("Please enter VIN to add vehicle to an existing user: "),
            call("Please enter the color (6 digit HEX code if possible) of vehicle: ")
        ])
        mock_vin_class.assert_called_once_with("TESTVIN123")
        self.mock_peek_function_for_assertions.assert_any_call(f"Make: {mock_vehicle_instance.Make}, Model: {mock_vehicle_instance.Model}, Year: {mock_vehicle_instance.ModelYear}")
        mock_database_constructor.assert_has_calls([call("DMufflerLocalDev.db"),call("DMufflerDatabase.db")], any_order=False)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('Main.Database')
    @patch('Main.integration_test')
    def test_testing_mode(self, mock_main_integration_test_func, mock_database_constructor, mock_parse_args):
        mock_parse_args.return_value = argparse.Namespace(mode=['TESTING'])
        mock_dev_db_instance = MagicMock(spec=Database); mock_prod_db_instance = MagicMock(spec=Database)
        mock_database_constructor.side_effect = [mock_dev_db_instance, mock_prod_db_instance]

        original_argv = sys.argv
        sys.argv = ['Main.py', '--mode', 'TESTING']
        if 'Main' in sys.modules: del sys.modules['Main']
        import Main as MainExecutable
        MainExecutable.Database = mock_database_constructor
        MainExecutable.integration_test = mock_main_integration_test_func
        MainExecutable.peek = sys.modules['peek'] # Explicitly use the mocked peek
        sys.argv = original_argv

        self.mock_peek_function_for_assertions.assert_any_call("DMuffler booting in TESTING mode", color="red")
        mock_main_integration_test_func.assert_called_once_with(mock_dev_db_instance)
        mock_database_constructor.assert_has_calls([call("DMufflerLocalDev.db"),call("DMufflerDatabase.db")], any_order=False)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('Main.Database')
    @patch('Main.main')
    def test_production_mode(self, mock_main_main_func, mock_database_constructor, mock_parse_args):
        mock_parse_args.return_value = argparse.Namespace(mode=['PRODUCTION'])
        mock_dev_db_instance = MagicMock(spec=Database); mock_prod_db_instance = MagicMock(spec=Database)
        mock_database_constructor.side_effect = [mock_dev_db_instance, mock_prod_db_instance]

        original_argv = sys.argv
        sys.argv = ['Main.py', '--mode', 'PRODUCTION']
        if 'Main' in sys.modules: del sys.modules['Main']
        import Main as MainExecutable
        MainExecutable.Database = mock_database_constructor
        MainExecutable.main = mock_main_main_func
        MainExecutable.peek = sys.modules['peek'] # Explicitly use the mocked peek
        sys.argv = original_argv

        self.mock_peek_function_for_assertions.assert_any_call("DMuffler booting in standard PRODUCTION mode", color="green")
        mock_main_main_func.assert_called_once_with(mock_prod_db_instance)
        mock_database_constructor.assert_has_calls([call("DMufflerLocalDev.db"),call("DMufflerDatabase.db")], any_order=False)

    # No @patch for ESPS here. Rely on sys.modules mocks for sounddevice and pynput.
    # The MainModule.integration_test will call the *real* ESPS.
    # We also need to mock pynput.keyboard.Listener for the real ESPS.unit_test()
    @patch('pynput.keyboard.Listener') # This will be used by the real ESPS.unit_test()
    def test_main_integration_test_function(self, mock_pynput_listener):
        # mock_pynput_listener is the mock for pynput.keyboard.Listener class
        mock_listener_instance = MagicMock()
        mock_pynput_listener.return_value = mock_listener_instance # Listener() returns our mock instance

        # MainModule uses the real ESPS, which uses the globally mocked sounddevice and pynput.
        MainModule.integration_test()

        # We can't easily assert ESPS constructor was called without patching ESPS itself.
        # But we can check if sounddevice.OutputStream (mocked globally) was called by real ESPS.
        mock_sd_module_global.OutputStream.assert_called()
        # And if the listener was started
        mock_pynput_listener.assert_called_once()
        mock_listener_instance.start.assert_called_once()


    def test_main_function_pass_through(self):
        mock_db = MagicMock(spec=Database)
        try:
            MainModule.main(mock_db)
        except Exception as e:
            self.fail(f"Main.main(db) raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
