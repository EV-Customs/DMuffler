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

## Standard Python libraries
import os                           # TODO
from dataclasses import dataclass   # TODO
from typing import List             # TODO

# Global print() statement toggle for entire DMuffler library
DEBUG_STATEMENTS_ON = True


@dataclass(frozen=True)
class SupportedVehicle:
    """ Defines supported vehicles that DMuffler app can run inside.
    """
    make:  str  # e.g. Ford, Tesla
    model: str  # e.g. Mustang, Model 3
    year:  int  # Manufacture Year

# Electrical Vehicle (EV) and hybrid vehicles makes supported by DMuffler
TESLA = "Tesla"
APTERA = "Aptera"
KIA = "Kia"
RIVIAN = "Rivian"
FORD = "Ford"
VINFAST = "VINFAST"

SUPPORTED_VEHICLES: List[SupportedVehicle] = [
        SupportedVehicle(TESLA, "Model 3",  2023),
        SupportedVehicle(APTERA, "Atera", 2023),
        SupportedVehicle(KIA, "Niro", 2023),
        SupportedVehicle(RIVIAN, "R1T", 2023),
        SupportedVehicle(FORD, "Mustang Mach-E", 2023),
        SupportedVehicle(VINFAST, "VF 8", 2023)
]

@dataclass(frozen=True)
class VehicleAsset:
    """ Defines canonical image and sound asset paths of all digital vehicles in DMuffler.
    """
    engineSoundID: int  # Unique Sound ID to let embedded software communicate with mobile app
    name: str           # Car name for User Interfaces (UI's)
    image: str          # Relative file path to .png image assets
    sound: str          # Relative file path to .wav image assets

# Internal Combustion Enginer (ICE) car engine sound CONSTANTS
# UPDATE the following CarAsset List and ../sounds & ../images folders to add new ICE sounds
MC_LAREN_F1 = 0
LA_FERRARI = 1
PORCSHE_911 = 2
BMW_M4 = 3
JAGUAR_E_TYPE_SERIES_1 = 4
FORD_MODEL_T = 5
FORD_MUSTANG_GT350 = 6

VEHICLE_ASSETS: List[VehicleAsset] = [
    VehicleAsset(MC_LAREN_F1, "McLaren F1", "static/images/McLarenF1.png", "static/sounds/McLarenF1.wav"),
    VehicleAsset(LA_FERRARI, "Ferrari LaFerrari", "static/images/LaFerrari.png", "static/sounds/LaFerrari.wav"),
    VehicleAsset(PORCSHE_911, "Porsche 911", "static/images/Porsche911.png", "static/sounds/Porsche911.wav"),
    VehicleAsset(BMW_M4, "BMW M4", "static/images/BMW_M4.png", "static/sounds/BMW_M4.wav"),
    VehicleAsset(JAGUAR_E_TYPE_SERIES_1, "Jaguar E-Type", "static/images/JaguarEtypeSeries1.png", "static/sounds/JaguarEtypeSeries1.wav"),
    VehicleAsset(FORD_MODEL_T, "Ford Model T", "static/images/FordModelT.png", "static/sounds/FordModelT.wav"),
    VehicleAsset(FORD_MUSTANG_GT350, "Ford Mustang GT350", "static/images/FordMustangGT350.png", "static/sounds/FordMustangGT350.wav"),
    # TODO VehicleAsset("star_wars_podracer", "static/images/STAR_WARS_PODRACER.png", "static/sounds/STAR_WARS_PODRACER.mp3"),
    # TODO VehicleAsset("subaru_wrx_sti", "static/images/SUBARU_WRX_STI.png", "static/sounds/SUBARU_WRX_STI.mp3"),
]

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

# Datatbase Table Name & HTTP error code CONSTANTS
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

# Utility: Validate asset existence at startup
def validate_assets():
    """ Validate that sound and images file assets exist

    Arg(s):
        None

    Returns: Nothing
    """
    missing = []
    for asset in VEHICLE_ASSETS:
        if not os.path.isfile(asset.image):
            missing.append(asset.image)
        if not os.path.isfile(asset.sound):
            missing.append(asset.sound)
    if missing:
        raise FileNotFoundError(f"Missing asset files: {missing}")


if __name__ == "__main__":
    print(f"Open GlobalConstants.py to see CONSTANTS like {VEHICLE_ASSETS[BMW_M4].image} used in the EV Customs DMuffler library")
    validate_assets()
    print("Successfully exitting GlobalConstants.py")
