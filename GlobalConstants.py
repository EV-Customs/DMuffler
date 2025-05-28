#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__email__      = "dev@blazesanders.com"
__license__    = "MIT License"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "0.0.1"
__doc__        = "Useful global constants for the entire EV Customs DMuffler library"
"""

import os
from dataclasses import dataclass
from typing import List

# Global print() statement toggle for entire DMuffler library
DEBUG_STATEMENTS_ON = True

# Internal Combustion Enginer (ICE) car engine sound CONSTANTS
# Standardized to lowercase with underscores and .wav extension
# UPDATE this dictionary and DMuffler/static/sounds folder to add new ICE sounds
MC_LAREN_F1 = "mc_laren_f1.wav"
LA_FERRARI = "la_ferrari.wav"
PORSCHE_911 = "porsche_911.wav" # Corrected typo from PORCSHE to PORSCHE
BMW_M4 = "bmw_m4.wav"
JAGUAR_E_TYPE_SERIES_1 = "jaguar_e_type_series_1.wav"
FORD_MODEL_T = "ford_model_t.wav"
FORD_MUSTANG_GT350 = "ford_mustang_gt350.wav"

# A 'Collection' of valid sounds filenames and their engineSoundID (int): Unique Sound ID to let embedded software communicate with mobile app
# Keys are updated to reflect standardized filenames
EngineSoundsDict = {
    MC_LAREN_F1: 0, # "mc_laren_f1.wav": 0
    LA_FERRARI: 1,  # "la_ferrari.wav": 1
    PORSCHE_911: 2, # "porsche_911.wav": 2 (Corrected typo)
    BMW_M4: 3,      # "bmw_m4.wav": 3
    JAGUAR_E_TYPE_SERIES_1: 4, # "jaguar_e_type_series_1.wav": 4
    FORD_MODEL_T: 5, # "ford_model_t.wav": 5
    FORD_MUSTANG_GT350: 6 # "ford_mustang_gt350.wav": 6
}

# Vehicle make name CONTSTANTS - Yes these are sorted best to worst :)
TESLA = 0
APTERA = 1
KIA = 2
RIVIAN = 3
FORD = 4
VINFAST = 5

"""
Defines canonical image and sound asset paths for all supported cars in DMuffler.
All constants are grouped in the CarAsset dataclass for clarity and validation.
Use validate_assets() at startup to ensure all referenced assets exist.
"""

@dataclass(frozen=True)
class CarAsset:
    name: str  # Canonical car name
    image: str  # Path to image asset
    sound: str  # Path to sound asset

# Canonical asset definitions
CAR_ASSETS: List[CarAsset] = [
    CarAsset("bmw_m4", os.path.join("static", "images", "bmw_m4.png"), os.path.join("static", "sounds", "bmw_m4.wav")),
    CarAsset("ferrari_laferrari", os.path.join("static", "images", "ferrari_laferrari.png"), os.path.join("static", "sounds", "ferrari_laferrari.wav")),
    CarAsset("ford_model_t", os.path.join("static", "images", "ford_model_t.png"), os.path.join("static", "sounds", "ford_model_t.wav")),
    CarAsset("ford_mustang", os.path.join("static", "images", "ford_mustang.png"), os.path.join("static", "sounds", "ford_mustang.wav")),
    CarAsset("jaguar_e_type", os.path.join("static", "images", "jaguar_e_type.png"), os.path.join("static", "sounds", "jaguar_e_type.wav")),
    CarAsset("mclaren_artura", os.path.join("static", "images", "mclaren_artura.png"), os.path.join("static", "sounds", "mclaren_artura.wav")), # Assuming mclaren_artura is distinct from mc_laren_f1
    CarAsset("porsche_911", os.path.join("static", "images", "porsche_911.png"), os.path.join("static", "sounds", "porsche_911.wav")),
    # STAR_WARS_PODRACER, SUBARU_WRX_STI, TESLA_ROADSTER names are uppercase in image/sound filenames. Standardizing to lowercase.
    CarAsset("star_wars_podracer", os.path.join("static", "images", "star_wars_podracer.png"), os.path.join("static", "sounds", "star_wars_podracer.wav")),
    CarAsset("subaru_wrx_sti", os.path.join("static", "images", "subaru_wrx_sti.png"), os.path.join("static", "sounds", "subaru_wrx_sti.wav")),
    CarAsset("tesla_roadster", os.path.join("static", "images", "tesla_roadster.png"), os.path.join("static", "sounds", "tesla_roadster.wav")),
]

# Legacy flat constants (for backward compatibility)
# Updated to use os.path.join and .wav for sounds, and standardized filenames for consistency
bmw_m4_img = os.path.join("static", "images", "bmw_m4.png")
bmw_m4_sound = os.path.join("static", "sounds", "bmw_m4.wav")
ferrari_laferrari_img = os.path.join("static", "images", "ferrari_laferrari.png")
ferrari_laferrari_sound = os.path.join("static", "sounds", "ferrari_laferrari.wav")
ford_model_t_img = os.path.join("static", "images", "ford_model_t.png")
ford_model_t_sound = os.path.join("static", "sounds", "ford_model_t.wav")
ford_mustang_img = os.path.join("static", "images", "ford_mustang.png")
ford_mustang_sound = os.path.join("static", "sounds", "ford_mustang.wav")
jaguar_e_type_img = os.path.join("static", "images", "jaguar_e_type.png")
jaguar_e_type_sound = os.path.join("static", "sounds", "jaguar_e_type.wav")
mclaren_artura_img = os.path.join("static", "images", "mclaren_artura.png")
mclaren_artura_sound = os.path.join("static", "sounds", "mclaren_artura.wav")
porsche_911_img = os.path.join("static", "images", "porsche_911.png")
porsche_911_sound = os.path.join("static", "sounds", "porsche_911.wav")
# Standardizing legacy constant names for image/sound files to lowercase
star_wars_podracer_img = os.path.join("static", "images", "star_wars_podracer.png")
star_wars_podracer_sound = os.path.join("static", "sounds", "star_wars_podracer.wav")
subaru_wrx_sti_img = os.path.join("static", "images", "subaru_wrx_sti.png")
subaru_wrx_sti_sound = os.path.join("static", "sounds", "subaru_wrx_sti.wav")
tesla_roadster_img = os.path.join("static", "images", "tesla_roadster.png")
tesla_roadster_sound = os.path.join("static", "sounds", "tesla_roadster.wav")

# The commented-out block of old sound constants has been removed.

# Utility: Validate asset existence at startup
def validate_assets():
    missing = []
    for asset in CAR_ASSETS:
        if not os.path.isfile(asset.image):
            missing.append(asset.image)
        if not os.path.isfile(asset.sound):
            missing.append(asset.sound)
    if missing:
        raise FileNotFoundError(f"Missing asset files: {missing}")


# Physical hardware CONTSTANTS
GO_PEDAL = 0                    # Pedal furthest right in the UK and USA
GO_PEDAL_POSITION_CAN_BUS_IDENTIFIER = [0b11_111_111_111]           #TODO or 29bit?

BRAKE_PEDAL = 1                 # Pedal furthest left in automatic transmissions in UK and USA
BRAKE_PEDAL_POSITION_CAN_BUS_IDENTIFIER = [0b11_111_111_111]        #TODO or 29bit?

# Digital simulation of hardware CONSTANTS
TOP_GEAR = 5
MAX_RPM = 10_000

# Tesla CAN Bus CONSTANTS
VELOCITY_SENSOR_CAN_BUS_IDENTIFIER = [0b111_1111_1111]             #TODO or 29bit?
ENGINE_LOAD_CAN_BUS_IDENTIFIER = [0b111_1111_1111]                 #TODO or 29bit?
RPM_CAN_BUS_IDENTIFIER = [0b111_1111_1111]                         #TODO or 29bit?

ODDOMETER_CAN_BUS_IDENTIFIER = [0b111_1111_1111]                   #TODO or 29bit?
HYBRID_BATTERY_REMAINING_CAN_BUS_IDENTIFIER = [0b111_1111_1111]    #TODO or 29bit?

# User Interface CONSTANTS
UI_TERMINAL_DELAY = 0.1         # Units are seconds
MAX_UI_DELAY = 2.0              # Units are seconds
FUNCTION_DELAY = 0.005          # Units are seconds
MIN_CAN_BUS_TIMESTEP = 0.001    # Units are seconds
STANDARD_POLLING_RATE = 0.5     # Units are Hertz (0.5 Hz == 33.3 ms)
COLLECTING_DATA = False         # Software database flag to protect user data
SECURITY_TOGGLE_PIN = 4         # Hardware GPIO pin number to protect user data at hardware level TODO
ERROR_LEVEL_LOG = 1
WARNING_LEVEL_LOG = 2

# Text to Voice Audio CONSTANTS
FEMALE_ENGLISH_1 = "TODO"               # Used in VoiceGenerator http://www.festvox.org/flite/packed/flite-2.0/voices/
MALE_ENGLISH_1 = "TODO"                 # Used in VoiceGenerator http://www.festvox.org/flite/packed/flite-2.0/voices/
DIPHONE_MODEL_TECHNIQUE = "TODO"        # Most robotic sounding model, see https://github.com/MycroftAI/mimic1#notes
CLUSTER_GEN_MODEL_TECHNIQUE = "TODO"    # Most human sounding model with large file sizes and high CPU usage
HTS_MODEL_TECHNIQUE = "TODO"            # Semi-human sounding model with reduced files sizes

# Dimensional unit CONSTANTS
PERCENTAGE_UNITS = "%"
MILLIMETER_UNITS = "mm"
CENTIMETER_UNITS = "cm"

# Datatbase Table Name & HTTP error code  CONSTANTS
DATABASE_TABLE_NAMES = ["Users", "Vehicles", "EngineSounds", "TODO"]      #TODO
USERS_TABLE = 0
VEHICLES_TABLE = 1
ENGINE_SOUNDS_TABLE = 2
DATABASE_OPERATION_FAILED = 400
DATABASE_OPERATION_SUCCESFULL = 200
SNAPSHOT_SIZE = 1000                    # OTA Update payload size [0x00] * 1000

# OBD-2 wiring CONSTANTS with pin number on ODB-2 connector, pin name, and color of wire
# MD = Manufacturer's Discretion https://en.wikipedia.org/wiki/On-board_diagnostics#OBD-II_diagnostic_connector
PIN01_MD = "BROWN_WIRE"
PIN02_SAE_J1850_LINE_BUS_PLUS = "BROWN_WHITE_WIRE"
PIN03_MD = "PURPLE_WIRE"
PIN04_CHASSIS_GND = "ORANGE_WIRE"                                   # 1A - TIE TOGETHER TO REDUCE GROUND LOOPS?
PIN05_SIGNAL_GND = "TEAL_WIRE"  # AKA BABY BLUE                     # 1B - TIE TOGETHER TO REDUCE GROUND LOOPS?
PIN06_SAE_J2284_CAN_HIGH = "GREEN_WIRE"                             # 2
PIN07_K_LINE_ISO_9141_2__ISO_DIS_4230 = "BLACK_WIRE"
PIN08_MD = "BLACK_WHITE_WIRE"
PIN09_MD = "RED_WHITE_WIRE"
PIN10_SAE_J1850_LINE_BUS_MINUS = "WHIRE_WIRE"
PIN11_MD = "YELLOW_WIRE"
PIN12_MD = "PINK_WIRE"
PIN13_MD = "GREY_WIRE"
PIN14_SAE_J2284_CAN_LOW = "GREEN_WHITE_WIRE"                        # 3
PIN15_L_LINE_ISO_9141_2__ISO_DIS_4230_4 = "DARK_BLUE_WIRE"
PIN16_UNSWITCHED_VEHICLE_BATTERY_POSITIVE = "RED_WIRE"              # 4

# ODB-2 python-odb protocol_name() and protocol_id()
SAE_J1850_PWM = 1
SAE_J1850_VPW = 2

# The GlobalConstants class definition and its __main__ block have been removed
# as they were not serving a functional purpose for a constants file.
# If a specific action is needed when running this file directly,
# it can be placed at the module level under an if __name__ == "__main__": block.
