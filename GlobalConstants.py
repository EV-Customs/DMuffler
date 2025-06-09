#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT License"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "0.0.1"
__doc__        = "Useful global constants for the entire EV Customs DMuffler library"
"""

import os
from dataclasses import dataclass
from typing import List, Dict # Added Dict
from pathlib import Path # Added pathlib

# ==============================================================================
# Project Structure Constants
# ==============================================================================
PROJECT_ROOT: Path = Path(__file__).resolve().parent
STATIC_PATH: Path = PROJECT_ROOT / "static"
IMAGES_BASE_PATH: Path = STATIC_PATH / "images"
SOUNDS_BASE_PATH: Path = STATIC_PATH / "sounds"

# ==============================================================================
# Debugging & Logging Constants
# ==============================================================================
# Global print() statement toggle for entire DMuffler library
DEBUG_STATEMENTS_ON: bool = True
ERROR_LEVEL_LOG: int = 1
WARNING_LEVEL_LOG: int = 2

# ==============================================================================
# Engine Sound Asset Constants
# ==============================================================================
# Standardized to lowercase filenames with .wav extension
MCLAREN_F1_FILENAME: str = "mclaren_f1.wav"
LAFERRARI_FILENAME: str = "laferrari.wav"
PORSCHE_911_FILENAME: str = "porsche_911.wav"
BMW_M4_FILENAME: str = "bmw_m4.wav"
JAGUAR_E_TYPE_SERIES_1_FILENAME: str = "jaguar_e_type_series_1.wav"
FORD_MODEL_T_FILENAME: str = "ford_model_t.wav"
FORD_MUSTANG_GT350_FILENAME: str = "ford_mustang_gt350.wav"
STAR_WARS_PODRACER_FILENAME: str = "star_wars_podracer.wav" # Assuming .wav, was in CAR_ASSETS
SUBARU_WRX_STI_FILENAME: str = "subaru_wrx_sti.wav" # Assuming .wav, was in CAR_ASSETS
TESLA_ROADSTER_FILENAME: str = "tesla_roadster.wav" # Assuming .wav, was in CAR_ASSETS


# A 'Collection' of valid sounds filenames and their engineSoundID (int):
# Unique Sound ID to let embedded software communicate with mobile app.
# UPDATE this dictionary and ensure corresponding files exist in SOUNDS_BASE_PATH
EngineSoundsDict: Dict[str, int] = {
    MCLAREN_F1_FILENAME: 0,
    LAFERRARI_FILENAME: 1,
    PORSCHE_911_FILENAME: 2,
    BMW_M4_FILENAME: 3,
    JAGUAR_E_TYPE_SERIES_1_FILENAME: 4,
    FORD_MODEL_T_FILENAME: 5,
    FORD_MUSTANG_GT350_FILENAME: 6,
    # STAR_WARS_PODRACER_FILENAME: 7, # Example if adding more
    # SUBARU_WRX_STI_FILENAME: 8,
    # TESLA_ROADSTER_FILENAME: 9,
}

# ==============================================================================
# Car Asset Definitions (Images and Sounds)
# ==============================================================================
@dataclass(frozen=True)
class CarAsset:
    name: str      # Canonical car name
    image: Path    # Absolute path to image asset
    sound: Path    # Absolute path to sound asset

# Canonical asset definitions using absolute paths
CAR_ASSETS: List[CarAsset] = [
    CarAsset("bmw_m4", IMAGES_BASE_PATH / BMW_M4_FILENAME.replace(".wav", ".png"), SOUNDS_BASE_PATH / BMW_M4_FILENAME), # Assuming image name matches sound name
    CarAsset("ferrari_laferrari", IMAGES_BASE_PATH / LAFERRARI_FILENAME.replace(".wav", ".png"), SOUNDS_BASE_PATH / LAFERRARI_FILENAME),
    CarAsset("ford_model_t", IMAGES_BASE_PATH / FORD_MODEL_T_FILENAME.replace(".wav", ".png"), SOUNDS_BASE_PATH / FORD_MODEL_T_FILENAME),
    CarAsset("ford_mustang", IMAGES_BASE_PATH / "ford_mustang_gt350.png", SOUNDS_BASE_PATH / FORD_MUSTANG_GT350_FILENAME), # Specific image name
    CarAsset("jaguar_e_type", IMAGES_BASE_PATH / JAGUAR_E_TYPE_SERIES_1_FILENAME.replace(".wav", ".png"), SOUNDS_BASE_PATH / JAGUAR_E_TYPE_SERIES_1_FILENAME),
    CarAsset("mclaren_artura", IMAGES_BASE_PATH / "mclaren_artura.png", SOUNDS_BASE_PATH / MCLAREN_F1_FILENAME), # Artura image, F1 sound
    CarAsset("porsche_911", IMAGES_BASE_PATH / PORSCHE_911_FILENAME.replace(".wav", ".png"), SOUNDS_BASE_PATH / PORSCHE_911_FILENAME),
    CarAsset("star_wars_podracer", IMAGES_BASE_PATH / "STAR_WARS_PODRACER.png", SOUNDS_BASE_PATH / STAR_WARS_PODRACER_FILENAME), # Uppercase image
    CarAsset("subaru_wrx_sti", IMAGES_BASE_PATH / "SUBARU_WRX_STI.png", SOUNDS_BASE_PATH / SUBARU_WRX_STI_FILENAME), # Uppercase image
    CarAsset("tesla_roadster", IMAGES_BASE_PATH / "TESLA_ROADSTER.png", SOUNDS_BASE_PATH / TESLA_ROADSTER_FILENAME), # Uppercase image
]

# ==============================================================================
# Asset Validation Utility
# ==============================================================================
def validate_assets():
    """
    Validates the existence of asset files defined in CAR_ASSETS and EngineSoundsDict.
    Uses absolute paths derived from Path objects.
    """
    missing_assets = []

    # Validate assets from CAR_ASSETS (paths are already absolute Path objects)
    for asset in CAR_ASSETS:
        if not asset.image.is_file():
            missing_assets.append(f"{asset.name} image: {asset.image}")

        if not asset.sound.is_file():
            missing_assets.append(f"{asset.name} sound: {asset.sound}")

    # Validate sound files from EngineSoundsDict
    # Construct absolute paths for these and ensure they are checked if not already covered by CAR_ASSETS
    car_asset_sound_paths = {asset.sound for asset in CAR_ASSETS}

    for sound_filename in EngineSoundsDict.keys():
        dict_sound_path = SOUNDS_BASE_PATH / sound_filename
        if dict_sound_path not in car_asset_sound_paths: # Check if already validated via CAR_ASSETS
            if not dict_sound_path.is_file():
                missing_assets.append(f"EngineSoundsDict sound: {dict_sound_path}")

    if missing_assets:
        # Report missing files with paths relative to project root for user convenience
        missing_relative_paths = [str(Path(p.split(': ', 1)[1]).relative_to(PROJECT_ROOT)) if ': ' in p else str(Path(p).relative_to(PROJECT_ROOT)) for p in missing_assets]
        raise FileNotFoundError(f"Missing asset files (paths relative to project root): {missing_relative_paths}")

# ==============================================================================
# Vehicle Definition Constants
# ==============================================================================
# Vehicle make name CONTSTANTS
TESLA: int = 0
APTERA: int = 1
KIA: int = 2
RIVIAN: int = 3
FORD: int = 4
VINFAST: int = 5

# ==============================================================================
# Hardware Interface Constants (CAN Bus, GPIO)
# ==============================================================================
# Physical hardware CONTSTANTS
GO_PEDAL: int = 0      # Pedal furthest right in the UK and USA
# TODO: Critical - Verify CAN bus ID bitness (11-bit or 29-bit) and actual ID values.
# Using a placeholder list format, actual implementation might require single int or specific format.
GO_PEDAL_POSITION_CAN_BUS_IDENTIFIER: List[int] = [0b11_111_111_111] # Placeholder - Example for 11-bit ID

BRAKE_PEDAL: int = 1   # Pedal furthest left in automatic transmissions in UK and USA
BRAKE_PEDAL_POSITION_CAN_BUS_IDENTIFIER: List[int] = [0b11_111_111_111] # Placeholder - Example for 11-bit ID

# Tesla CAN Bus CONSTANTS (Examples, verify actual IDs and bitness)
# TODO: Critical - Verify all Tesla CAN Bus IDs and their bitness (11-bit or 29-bit).
VELOCITY_SENSOR_CAN_BUS_IDENTIFIER: List[int] = [0b111_1111_1111]      # Placeholder
ENGINE_LOAD_CAN_BUS_IDENTIFIER: List[int] = [0b111_1111_1111]          # Placeholder
RPM_CAN_BUS_IDENTIFIER: List[int] = [0b111_1111_1111]                  # Placeholder
ODDOMETER_CAN_BUS_IDENTIFIER: List[int] = [0b111_1111_1111]            # Placeholder
HYBRID_BATTERY_REMAINING_CAN_BUS_IDENTIFIER: List[int] = [0b111_1111_1111] # Placeholder

# GPIO Pins
# TODO: Define actual GPIO pin if this security feature is implemented.
SECURITY_TOGGLE_PIN: int = 4 # Placeholder GPIO pin number

# ==============================================================================
# Application Behavior Constants
# ==============================================================================
# Digital simulation of hardware CONSTANTS
TOP_GEAR: int = 5
MAX_RPM: int = 10_000

# User Interface CONSTANTS
UI_TERMINAL_DELAY: float = 0.1         # Units are seconds
MAX_UI_DELAY: float = 2.0              # Units are seconds
FUNCTION_DELAY: float = 0.005          # Units are seconds
MIN_CAN_BUS_TIMESTEP: float = 0.001    # Units are seconds
STANDARD_POLLING_RATE: float = 0.5     # Units are Hertz (0.5 Hz == 33.3 ms)

# Data Handling
COLLECTING_DATA: bool = False          # Software database flag to protect user data
SNAPSHOT_SIZE: int = 1000              # OTA Update payload size, e.g., [0x00] * 1000

# ==============================================================================
# Database Constants
# ==============================================================================
DATABASE_TABLE_NAMES: List[str] = ["Users", "Vehicles", "EngineSounds"]
USERS_TABLE: int = 0
VEHICLES_TABLE: int = 1
ENGINE_SOUNDS_TABLE: int = 2

DATABASE_OPERATION_FAILED: int = 400
DATABASE_OPERATION_SUCCESSFUL: int = 200 # Note: Typo "SUCCESFULL" corrected to "SUCCESSFUL"

# ==============================================================================
# Dimensional Unit Constants
# ==============================================================================
PERCENTAGE_UNITS: str = "%"
MILLIMETER_UNITS: str = "mm"
CENTIMETER_UNITS: str = "cm"

# ==============================================================================
# OBD-2 Protocol and Wiring Constants
# ==============================================================================
# OBD-2 wiring CONSTANTS with pin number on ODB-2 connector, pin name, and color of wire
# MD = Manufacturer's Discretion https://en.wikipedia.org/wiki/On-board_diagnostics#OBD-II_diagnostic_connector
PIN01_MD: str = "BROWN_WIRE"
PIN02_SAE_J1850_LINE_BUS_PLUS: str = "BROWN_WHITE_WIRE"
PIN03_MD: str = "PURPLE_WIRE"
PIN04_CHASSIS_GND: str = "ORANGE_WIRE"                                   # 1A - TIE TOGETHER TO REDUCE GROUND LOOPS?
PIN05_SIGNAL_GND: str = "TEAL_WIRE"  # AKA BABY BLUE                     # 1B - TIE TOGETHER TO REDUCE GROUND LOOPS?
PIN06_SAE_J2284_CAN_HIGH: str = "GREEN_WIRE"                             # 2
PIN07_K_LINE_ISO_9141_2__ISO_DIS_4230: str = "BLACK_WIRE"
PIN08_MD: str = "BLACK_WHITE_WIRE"
PIN09_MD: str = "RED_WHITE_WIRE"
PIN10_SAE_J1850_LINE_BUS_MINUS: str = "WHITE_WIRE" # Note: Typo "WHIRE_WIRE" corrected to "WHITE_WIRE"
PIN11_MD: str = "YELLOW_WIRE"
PIN12_MD: str = "PINK_WIRE"
PIN13_MD: str = "GREY_WIRE"
PIN14_SAE_J2284_CAN_LOW: str = "GREEN_WHITE_WIRE"                        # 3
PIN15_L_LINE_ISO_9141_2__ISO_DIS_4230_4: str = "DARK_BLUE_WIRE"
PIN16_UNSWITCHED_VEHICLE_BATTERY_POSITIVE: str = "RED_WIRE"              # 4

# ODB-2 python-odb protocol_name() and protocol_id()
SAE_J1850_PWM: int = 1
SAE_J1850_VPW: int = 2

# ==============================================================================
# Main Execution Block (Informational)
# ==============================================================================
# This class is not meant to be instantiated. Constants are accessed directly.
# class GlobalConstants: # This class wrapper is not conventional for a constants file.
#
#     if __name__ == "__main__":
#         print("Open GlobalConstants.py to see CONSTANTS used in the EV Customs DMuffler library")

if __name__ == "__main__":
    print("GlobalConstants.py contains constants for the DMuffler project.")
    print(f"Project Root determined as: {PROJECT_ROOT}")
    print(f"Sounds will be loaded from: {SOUNDS_BASE_PATH}")
    # Example of running validation if script is executed directly (optional)
    # try:
    #     validate_assets()
    #     print("Asset paths validated successfully (simulated for direct run, ensure files exist for real check).")
    # except FileNotFoundError as e:
    #     print(f"Asset validation failed: {e}")
