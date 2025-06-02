# dmuffler_pi.py
#
# Purpose:
# This script is designed to run on a Raspberry Pi equipped with a PiCAN HAT and an I2S DAC.
# It captures CAN bus data, specifically focusing on engine RPM, to dynamically adjust
# audio playback, simulating an active exhaust system.
#
# Raspberry Pi Setup Overview:
# - PiCAN HAT: Used for interfacing with the CAN bus of a vehicle to read data like RPM.
# - I2S DAC: An audio digital-to-analog converter that provides high-quality sound output.
#   This script will send audio data to this DAC.
#
# Manual Setup Steps (to be detailed later):
# - Configuration of the CAN interface.
# - Installation of necessary Python libraries.
# - Setting up the I2S DAC.
# - Preparing audio files.

# ==============================================================================
# HOW TO RUN THE SCRIPT
# ==============================================================================
# 1. Ensure all hardware (PiCAN HAT, I2S DAC) is connected and configured
#    as described in the "HARDWARE SETUP" sections below.
#
# 2. Ensure system packages and Python packages are installed, preferably in
#    a virtual environment (see "SYSTEM PACKAGE INSTALLATION" and
#    "PYTHON PACKAGE INSTALLATION" sections).
#
# 3. Activate your virtual environment (if you created one):
#    source dmp_env/bin/activate  # Or your venv name
#
# 4. The script may require sudo privileges for certain operations:
#    - Bringing up the CAN interface (`sudo ip link set can0...`).
#    - Accessing certain hardware directly (less common with overlays).
#    The script attempts to run the `ip link set` command using `sudo`.
#    If you prefer to manage the CAN interface manually, ensure it's up before running:
#    sudo ip link set can0 up type can bitrate 500000 # Adjust params as needed
#    Then you might be able to run the script without sudo, depending on permissions.
#
# 5. Run the script:
#    python3 dmuffler_pi.py [OPTIONS]
#
#    Common options:
#    --can-interface can0       Specify CAN interface.
#    --rpm-can-id 0CFEF100      Specify the CAN ID for RPM data (in hex).
#    --rpm-byte-index 3         Specify the starting byte index for RPM data in the CAN frame.
#    --rpm-scale-factor 0.125   Specify the scale factor for RPM calculation.
#    --audio-path ./sounds/     Directory containing RPM-named WAV files (e.g., 1000rpm.wav).
#    --audio-device-index 1     Manually specify audio output device index if auto-detect fails.
#    --test-mode                Run in test mode without live CAN bus.
#    --debug                    Enable verbose debug messages.
#    --no-audio                 Disable audio output.
#
#    Use `python3 dmuffler_pi.py --help` to see all available options.
#
# ==============================================================================
# EXPECTED CONSOLE OUTPUT (Examples)
# ==============================================================================
#
# On successful start with live CAN and auto-detected audio:
#   Debug mode enabled.
#   Initial arguments: Namespace(...)
#   Loaded audio files for RPMs: [800, 1000, 1500, ...]
#   No audio device index specified. Attempting to find I2S DAC or suitable output...
#     Checking output device 0: ...
#     Checking output device 1: ...
#   Found potential DAC/Output: 'XYZ DAC (card 1, device 0)' at index 1. Using this device.
#   Attempting to open audio stream on device index 1 ('XYZ DAC (card 1, device 0)')
#     Using Sample Rate: 44100, Channels: 2, Chunk Size: 1024
#   Audio stream opened successfully on device index 1 ('XYZ DAC (card 1, device 0)').
#   Attempting to bring up CAN interface can0 at 500000 bps...
#   Debug: CAN interface can0 brought up at 500000 bps via ip link.
#   Successfully initialized CAN bus on channel 'can0' with filters: [{'can_id': 0x123, 'can_mask': 2047, 'extended': False}]
#   Listening for CAN messages on 'can0' for RPM ID 0x123...
#   DMuffler application started. Press Ctrl+C to exit.
#   Min RPM: 1000, Max RPM: 8000, Loop Delay: 0.02s
#   Audio files map (RPM:filepath): {1000: 'audio/1000rpm.wav', ...}
#   Debug: Received CAN message. ID: 0x123, Data: ..., Raw RPM Val: ..., Scaled RPM: ...
#   [MainLoop] RPM: 1250. Target audio: 'audio/1000rpm.wav'. Starting new audio thread.
#   [AudioThread:AudioPlayerThread-1000rpm.wav] Attempting to play audio/1000rpm.wav
#   ...
#
# On start with --test-mode:
#   --- RUNNING IN TEST MODE ---
#   Live CAN bus interaction is disabled. RPM will be simulated...
#   DMuffler application started in Test Mode. Press Ctrl+C to exit.
#   Min RPM: 1000, Max RPM: 8000, Loop Delay: 0.02s
#   Audio files map (RPM:filepath): {1000: 'audio/1000rpm.wav', ...}
#   [Test Mode] Simulated RPM: 1050
#   [MainLoop] RPM: 1050. Target audio: 'audio/1000rpm.wav'. Starting new audio thread.
#   ...
#
# If CAN initialization fails:
#   ERROR: Failed to bring up CAN interface 'can0' using 'ip link' command: ...
#   Falling back to Test Mode due to CAN interface setup failure.
#   --- RUNNING IN TEST MODE ---
#   ...
#
# If audio file is missing during playback:
#   [AudioThread:AudioPlayerThread-...] ERROR: WAV file not found: audio/nonexistent.wav
#
# On exit (Ctrl+C):
#   Program interrupted by user. Cleaning up...
#   Cleaning up resources...
#   Signaling audio thread to stop...
#   Waiting for AudioPlayerThread-... to complete...
#   AudioPlayerThread-... completed.
#   Main shared audio stream (if used) stopped and closed.
#   PyAudio instance terminated.
#   CAN bus shutdown.
#   DMuffler application exited.
#
# ==============================================================================

# --- SYSTEM SETUP INSTRUCTIONS ---

# SYSTEM PACKAGE INSTALLATION
# ---------------------------
# Ensure your Raspberry Pi OS is up to date and install necessary packages:
#
# sudo apt update
# sudo apt full-upgrade -y
# sudo apt install -y python3-pip python3-dev python3-venv git libasound2-dev
#
# Note: libasound2-dev is crucial for PyAudio compilation if installing from source.
#       If using pre-built wheels, it might not be strictly necessary but is good practice.

# VIRTUAL ENVIRONMENT SETUP
# -------------------------
# It's highly recommended to use a virtual environment to manage dependencies:
#
# python3 -m venv dmp_env
# source dmp_env/bin/activate
#
# To deactivate the environment later, simply type:
# deactivate

# PYTHON PACKAGE INSTALLATION
# ---------------------------
# Create a requirements.txt file with the following content:
#
# python-can==4.1.0
# pyaudio>=0.2.11  # Or the specific version you have tested, e.g., pyaudio==0.2.13
# pygame>=2.1.0    # For potential future enhancements or alternative audio/event handling
# numpy>=1.20.0    # For numerical operations, potentially audio processing
# scipy>=1.7.0     # For more advanced signal processing if needed
#
# Then, install these packages within your activated virtual environment:
# pip install -r requirements.txt
#
# Alternatively, to install packages individually:
# pip install python-can==4.1.0 pyaudio numpy scipy pygame

# ==============================================================================
# HARDWARE SETUP: SocketCAN (PiCAN HAT - MCP2515)
# ==============================================================================
# 1. Enable SPI and configure MCP2515 overlay in /boot/config.txt:
#    Make sure the following lines are present in your /boot/config.txt
#    (or /boot/firmware/config.txt on newer Raspberry Pi OS versions):
#
#    dtparam=spi=on
#    # dtoverlay=spi-bcm2835 # Often enabled by default, but good to ensure
#    dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
#
#    # The oscillator frequency might vary depending on your PiCAN HAT model (e.g., 8MHz or 16MHz).
#    # The interrupt pin might also vary. Check your HAT's documentation.
#    # After editing, reboot the Raspberry Pi: sudo reboot
#
# 2. Load CAN drivers (usually handled automatically if dtoverlay is correct):
#    After rebooting, the necessary kernel modules should load automatically.
#    You can verify with: lsmod | grep -E "mcp251x|can_dev"
#    If not loaded, you might need to load them manually (less common now):
#
#    # sudo modprobe mcp251x
#    # sudo modprobe can_dev
#
# 3. Bring up the CAN interface:
#    Configure the can0 interface with your desired bitrate (e.g., 500000 bps).
#    This command needs to be run after each boot, or added to a startup script (e.g., /etc/rc.local).
#
#    sudo ip link set can0 up type can bitrate 500000
#
# 4. Verify CAN interface:
#    Check if the interface is up: ip -details link show can0
#    Test with candump (install can-utils: sudo apt install can-utils):
#    candump can0
#    (You should see CAN traffic if your PiCAN HAT is connected to an active CAN bus)
#
# ==============================================================================
# HARDWARE SETUP: Audio Output (I²S DAC HAT - e.g., HiFiBerry DAC+)
# ==============================================================================
# 1. Enable I²S and configure your DAC overlay in /boot/config.txt:
#    Make sure the following lines are present in your /boot/config.txt
#    (or /boot/firmware/config.txt on newer Raspberry Pi OS versions):
#
#    dtparam=i2s=on
#    dtoverlay=hifiberry-dac # Or your specific DAC overlay (e.g., hifiberry-dacplus, iqaudio-dac, etc.)
#
#    # Some overlays might disable onboard audio. If you need both, check DAC documentation.
#    # After editing, reboot the Raspberry Pi: sudo reboot
#
# 2. Verify DAC detection:
#    After rebooting, list playback hardware devices:
#    aplay -l
#
#    Look for your DAC in the list (e.g., card 1: sndrpihifiberry, device 0: HifiBerry DAC HiFi pcm5102a-hifi-0).
#    The script will try to find this device, but you might need to specify the device index.
#
# 3. ALSA Configuration (Optional but sometimes helpful):
#    You can set your I²S DAC as the default ALSA device by creating/editing /etc/asound.conf:
#
#    pcm.!default {
#      type hw
#      card sndrpihifiberry # Use the card name from 'aplay -l'
#    }
#    ctl.!default {
#      type hw
#      card sndrpihifiberry # Use the card name from 'aplay -l'
#    }
#
#    This can simplify device selection in applications.
# --- END SYSTEM SETUP INSTRUCTIONS ---

import can
import pyaudio
import wave
import time
import os
import sys
import random
import numpy
import subprocess
import argparse
import threading

# --- Argument Parsing ---
def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Dynamic Muffler Audio Control for Raspberry Pi")
    parser.add_argument(
        "--can-interface",
        type=str,
        default="can0",
        help="CAN interface name (e.g., can0, vcan0). Default: can0",
    )
    parser.add_argument(
        "--rpm-can-id",
        type=lambda x: int(x, 0), # Allows hex (0x) or decimal input
        default=0x123, # Example CAN ID, replace with actual
        help="CAN ID for engine RPM data (hex or decimal). Default: 0x123",
    )
    parser.add_argument(
        "--rpm-byte-index",
        type=int,
        default=0,
        help="Byte index in the CAN message payload for RPM data. Default: 0",
    )
    parser.add_argument(
        "--rpm-scale-factor",
        type=float,
        default=1.0,
        help="Scaling factor to convert raw RPM CAN data to actual RPM. Default: 1.0",
    )
    parser.add_argument(
        "--audio-path",
        type=str,
        default="audio/",
        help="Path to the directory containing audio WAV files. Default: audio/",
    )
    parser.add_argument(
        "--min-rpm",
        type=int,
        default=1000,
        help="Minimum RPM threshold for starting audio playback. Default: 1000",
    )
    parser.add_argument(
        "--max-rpm",
        type=int,
        default=8000,
        help="Maximum RPM for audio playback adjustments. Default: 8000",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging for more verbose output.",
    )
    parser.add_argument(
        "--can-bitrate",
        type=int,
        default=500000,
        help="CAN bus bitrate (e.g., 250000, 500000). Default: 500000."
    )
    # It's good practice to have a test_mode argument for development
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode without live CAN bus initialization. Useful for testing audio logic."
    )
    # Adding rpm_offset as it was mentioned in the new CAN init block
    parser.add_argument(
        "--rpm-offset",
        type=float,
        default=0.0,
        help="Offset to add to the RPM value after scaling. Default: 0.0"
    )
    # Audio specific arguments that were previously assumed or implicitly part of init_audio
    parser.add_argument(
        "--audio-device-index",
        type=int,
        default=None, # Default to None to trigger auto-detection
        help="Audio output device index (from 'aplay -l'). Default: Auto-detect DAC."
    )
    parser.add_argument(
        "--audio-sample-rate",
        type=int,
        default=44100,
        help="Audio sample rate for the output stream. Default: 44100."
    )
    parser.add_argument(
        "--audio-channels",
        type=int,
        default=2, # Assuming stereo, common for DACs
        help="Audio channels for the output stream (1 for mono, 2 for stereo). Default: 2."
    )
    parser.add_argument(
        "--audio-chunk-size",
        type=int,
        default=1024,
        help="Number of frames per buffer for audio stream. Default: 1024."
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable all audio output. Useful for testing CAN logic only."
    )
    parser.add_argument(
        "--loop-delay",
        type=float,
        default=0.02, # 50Hz default
        help="Delay in seconds for the main application loop. Default: 0.02."
    )
    return parser.parse_args()

# --- Global Variables ---
# PyAudio instance (p) and stream are initialized in the main block if audio is enabled.
p_audio_instance = None
audio_stream = None # This is the main/shared stream, may not be used by threaded playback
audio_files = {} # Dictionary to store loaded audio files
can_bus = None # Will hold the python-can bus object

# Variables for threaded audio playback
audio_playback_thread = None
last_played_audio_file = None # To track the currently playing/selected audio file path

# --- Audio Functions ---
# NOTE ON AUDIO GENERATION: This script loads pre-recorded WAV files based on RPM.
# An alternative approach for more dynamic sound could be real-time audio synthesis
# using libraries like NumPy/SciPy to generate waveforms, or dedicated audio synthesis
# libraries, though this is more complex and CPU-intensive.
def load_audio_files(path, debug=False):
    """Loads WAV audio files from the specified directory."""
    loaded_files = {}
    if not os.path.isdir(path):
        print(f"Error: Audio path '{path}' not found or is not a directory.")
        return loaded_files

    for f in sorted(os.listdir(path)):
        if f.lower().endswith(".wav"):
            try:
                # Attempt to derive an RPM key from filename, e.g., "1000rpm.wav" -> 1000
                rpm_key = int(f.split("rpm")[0])
                loaded_files[rpm_key] = os.path.join(path, f)
            except ValueError:
                # Fallback if filename doesn't match expected RPM pattern
                # For now, we'll just print a warning and skip.
                # A more robust solution might assign them sequentially or use a manifest file.
                if debug:
                    print(f"Debug: Could not parse RPM from filename: {f}. Skipping.")
    if debug:
        print(f"Debug: Loaded audio files: {loaded_files}")
    if not loaded_files:
        print(f"Warning: No WAV files found in '{path}'.")
    return loaded_files

def init_audio(device_index=None, debug=False):
    """Initializes PyAudio and the output stream."""
    global p_audio_instance, audio_stream # Use the new global variable names
    # This function is now largely superseded by the main block's audio init logic
    # but play_audio_segment will still use the global audio_stream and p_audio_instance
    if not audio_stream: # Check the global stream variable
        if debug:
            print("Debug: init_audio called, but audio_stream is not set up (likely --no-audio or earlier error).")
        return

    # The actual stream opening is now done in the main block.
    # This function might be removed or refactored if it's no longer opening the stream.
    # For now, let's assume it's mostly a placeholder if stream opening is centralized.
    if debug:
        print("Debug: init_audio() called - stream should already be initialized if audio is enabled.")

# This is the original blocking playback function. It might be kept for specific uses
# or removed if all playback becomes threaded.
def play_audio_segment_blocking(wf_path, debug=False):
    """Plays a WAV file. This is a BLOCKING call."""
    global audio_stream, p_audio_instance # Use the new global variable names

    # This function assumes p_audio_instance and audio_stream (the main one) are initialized
    # if not args.no_audio. However, threaded playback typically creates its own stream.
    if args.no_audio or not p_audio_instance : # Check if PyAudio is available
        if debug and not args.no_audio:
            print("Debug: play_audio_segment_blocking called, but PyAudio not initialized or audio disabled.")
        return

    # If using the main shared stream:
    # if not audio_stream:
    #     if debug: print("Debug: Main audio stream not available for blocking playback.")
    #     return

    # For blocking playback, it's better to open/close its own stream to avoid conflicts
    # if the main 'audio_stream' was intended for something else (like callbacks).
    # However, the original code used the global 'audio_stream'.
    # Let's refine this to open its own stream for true blocking isolation.

    temp_stream = None
    wf = None
    try:
        wf = wave.open(wf_path, 'rb')
        temp_stream = p_audio_instance.open(
                        format=p_audio_instance.get_format_from_sample_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=args.audio_device_index # Use the configured device
                        # frames_per_buffer=args.audio_chunk_size # Already default in open
        )
        if debug:
            print(f"[Blocking] Playing {wf_path}")

        data = wf.readframes(args.audio_chunk_size)
        while len(data) > 0:
            temp_stream.write(data)
            data = wf.readframes(args.audio_chunk_size)

        temp_stream.wait_done() # Wait for all frames to be played
        if debug:
            print(f"[Blocking] Finished playing {wf_path}")

    except FileNotFoundError:
        print(f"[Blocking] Error: WAV file not found at {wf_path}")
    except Exception as e:
        print(f"[Blocking] Error playing audio segment {wf_path}: {e}")
    finally:
        if temp_stream:
            temp_stream.stop_stream()
            temp_stream.close()
        if wf:
            wf.close()


def play_audio_segment_threaded(wav_path, pya_instance, chunk_size, debug_flag):
    """
    Plays a WAV audio file in a separate thread.
    Each thread opens its own audio stream.
    """
    global audio_playback_thread # To update the global reference, and for the thread to check its status

    thread_wf = None
    thread_stream = None
    current_thread_obj = threading.current_thread()

    try:
        if debug_flag:
            print(f"[AudioThread:{current_thread_obj.name}] Attempting to play {wav_path}")

        thread_wf = wave.open(wav_path, 'rb')

        # Open a new stream for this thread
        # This ensures that each sound plays on its own dedicated stream,
        # preventing conflicts if sounds overlap or if main stream parameters are different.
        thread_stream = pya_instance.open(
            format=pya_instance.get_format_from_sample_width(thread_wf.getsampwidth()),
            channels=thread_wf.getnchannels(),
            rate=thread_wf.getframerate(),
            output=True,
            output_device_index=args.audio_device_index, # Use configured device index
            frames_per_buffer=chunk_size
        )

        if debug_flag:
            print(f"[AudioThread:{current_thread_obj.name}] Stream opened for {wav_path}. Channels={thread_wf.getnchannels()}, Rate={thread_wf.getframerate()}")

        data = thread_wf.readframes(chunk_size)
        while len(data) > 0:
            # Check if this thread is still the active one, or if it should stop
            # This allows a new sound to effectively "interrupt" this one if audio_playback_thread is set to new thread.
            if audio_playback_thread != current_thread_obj:
                if debug_flag:
                    print(f"[AudioThread:{current_thread_obj.name}] Playback of {wav_path} interrupted by new audio thread.")
                break
            thread_stream.write(data)
            data = thread_wf.readframes(chunk_size)

        if audio_playback_thread == current_thread_obj: # Only print if not interrupted
             if debug_flag:
                print(f"[AudioThread:{current_thread_obj.name}] Finished playing {wav_path}")

    except FileNotFoundError:
        print(f"[AudioThread:{current_thread_obj.name}] ERROR: WAV file not found: {wav_path}")
    except Exception as e:
        # Catching PyAudioError specifically can be useful too: `except pyaudio.PyAudioError as e:`
        print(f"[AudioThread:{current_thread_obj.name}] ERROR playing {wav_path}: {e}")
        import traceback
        if debug_flag: traceback.print_exc()
    finally:
        if thread_stream:
            try:
                if thread_stream.is_active(): # Check if stream is active before stopping
                    thread_stream.stop_stream()
                thread_stream.close()
                if debug_flag:
                     print(f"[AudioThread:{current_thread_obj.name}] Stream closed for {wav_path}")
            except Exception as e:
                if debug_flag:
                    print(f"[AudioThread:{current_thread_obj.name}] Error closing stream for {wav_path}: {e}")
        if thread_wf:
            thread_wf.close()

        # If this thread was the designated audio_playback_thread, clear it as it's now done.
        if audio_playback_thread == current_thread_obj:
            audio_playback_thread = None
            if debug_flag:
                print(f"[AudioThread:{current_thread_obj.name}] Cleared as active audio thread.")


# Original play_audio_segment, now potentially a wrapper or unused if direct threading is preferred
def play_audio_segment(wf_path, debug=False):
    """Plays a segment of a WAV file. For now, plays the whole file."""
    # This function will now be a simple wrapper to call the blocking version
    # or could be removed if only threaded playback is used from the main loop.
    # For now, let it call the blocking one to maintain original name if something still uses it.
    # The main loop will be updated to use `play_audio_segment_threaded` via `threading.Thread`.

    if debug:
        print(f"Debug: play_audio_segment called for {wf_path}. Defaulting to blocking playback for now.")
    play_audio_segment_blocking(wf_path, debug)

    # If args.no_audio or not audio_stream: # Check if audio is disabled or stream not available
    #    if debug and not args.no_audio: # Only print if not intentionally disabled
    #        print("Debug: play_audio_segment called, but audio stream not initialized or audio disabled.")
        return

    try:
        with wave.open(wf_path, 'rb') as wf:
            # Dynamic stream parameter adjustment based on WAV file
            # This makes the script more flexible with different WAV file formats.
            # It's important that the initial stream parameters (sample_rate, channels)
            # are either standard or this re-opening logic is robust.

            required_format = p_audio_instance.get_format_from_sample_width(wf.getsampwidth())
            required_channels = wf.getnchannels()
            required_rate = wf.getframerate()

            # Check if stream needs to be reopened with new parameters
            # This is a simplified check. A more robust check would compare all relevant params.
            # For now, we assume play_audio_segment will use the initially configured stream
            # and WAV files should ideally match these settings (sample rate, channels).
            # Re-opening stream per file can cause glitches.
            # A better approach for varying file formats is to resample/reformat audio files
            # to a common standard before running the script, or use a more advanced audio library.

            # For simplicity, let's assume the stream opened in main is sufficient for all files.
            # If not, the user should ensure WAV files match args.audio_sample_rate and args.audio_channels.
            # The following block for re-opening is commented out to prefer a stable stream.
            # If re-opening is desired, it needs careful management of stream state.
            pass # Original logic for play_audio_segment_blocking is now self-contained or done in threaded version.
            # The original play_audio_segment's internal logic was comparing WAV params to main stream.
            # This is less relevant if threads open their own streams based on WAV params.

            # Use the globally configured chunk size (now passed as an argument to threaded func)
            # chunk_size = args.audio_chunk_size
            data = wf.readframes(chunk_size)
            if debug:
                print(f"Debug: Playing {wf_path} (Channels: {wf.getnchannels()}, Rate: {wf.getframerate()}, Width: {wf.getsampwidth()})")

            while data:
                stream.write(data)
                data = wf.readframes(chunk_size)
            if debug:
                print(f"Debug: Finished playing {wf_path}")

    except FileNotFoundError:
        print(f"Error: Audio file not found: {wf_path}")
    except Exception as e:
        print(f"Error playing audio file {wf_path}: {e}")


def get_audio_file_for_rpm(rpm, available_audio_files, min_rpm, max_rpm, debug=False):
    """
    Selects an appropriate audio file based on the current RPM.
    This is a placeholder and will need more sophisticated logic.
    For now, it finds the closest RPM key in available_audio_files.
    """
    if not available_audio_files:
        return None

    if rpm < min_rpm:
        return None # Below threshold, no sound

    # Find the best RPM key (closest available RPM sound)
    # This simple logic picks the file with RPM key <= current RPM.
    # If multiple such files exist, it picks the one with the largest RPM key.
    # If no such file exists (e.g., current RPM is lower than any file's RPM key),
    # it could pick the lowest RPM sound or remain silent.

    suitable_rpm_keys = [r for r in available_audio_files.keys() if r <= rpm]
    if not suitable_rpm_keys:
        # This block handles the case where current RPM is lower than any RPM key
        # associated with an audio file (e.g., RPM is 1200, files start at 1500rpm).
        # However, we still want sound if current RPM is above the global 'min_rpm' threshold.
        if rpm >= min_rpm:
            # Fallback strategy: Find the audio file whose RPM key is numerically closest
            # to the current RPM. This provides a sound instead of silence.
            # Example: RPM=1200, min_rpm=1000, files={1500:"1500.wav", 2000:"2000.wav"}
            # This will select "1500.wav".
            closest_rpm_key = min(available_audio_files.keys(), key=lambda r_key: abs(r_key - rpm))
            if debug:
                print(f"Debug: RPM {rpm:.0f} is below any direct mapped RPM key but above min_rpm. "
                      f"Playing sound for numerically closest RPM: {closest_rpm_key} "
                      f"(file: {available_audio_files[closest_rpm_key]}).")
            return available_audio_files[closest_rpm_key]
        # If RPM is below min_rpm or the above fallback condition isn't met (e.g., no audio files at all, though caught earlier).
        if debug and rpm < min_rpm :
             print(f"Debug: RPM {rpm:.0f} is below min_rpm ({min_rpm}). No audio will be played.")
        return None # Explicitly return None if no suitable file found after all checks.


    best_match_rpm = max(suitable_rpm_keys) # Gets the highest RPM key that is less than or equal to current RPM.
    selected_file = available_audio_files[best_match_rpm]

    if debug:
        print(f"Debug: For RPM {rpm}, selected audio file for {best_match_rpm} RPM: {selected_file}")
    return selected_file


def cleanup_audio():
    """Cleans up PyAudio resources."""
    global audio_stream, p_audio_instance # Use new global names
    # This function is now effectively handled by the main script's finally block.
    # Kept for conceptual separation if we ever need more complex audio-specific cleanup.
    if debug:
        print("Debug: cleanup_audio() called. Actual cleanup in main's finally block.")
    # Actual cleanup happens in the main `finally` block to ensure p_audio_instance and audio_stream are handled.

# The 'can_bus' variable will be assigned in the main block.

# --- CAN Functions ---
# The init_can and cleanup_can functions are now integrated into the main block for clarity
# and to handle the new subprocess logic for bringing the interface up.

# NOTE ON VEHICLE PARAMETERS: This script primarily focuses on RPM for sound generation.
# To incorporate other parameters like throttle position, vehicle speed, or gear:
# 1. Identify their respective CAN IDs, data byte(s), and encoding (byte order, position, scaling, offset).
# 2. Add new command-line arguments (e.g., --throttle-can-id, --throttle-byte-index, etc.)
#    or use a configuration file for these additional parameters.
# 3. Extend the `get_rpm_from_can_message` function or, more likely, add new specific functions
#    (e.g., `get_throttle_position_from_can_message`) to parse these additional data points.
# 4. Modify the sound selection logic (e.g., `get_audio_file_for_rpm` or a new function)
#    and/or audio playback characteristics (volume, effects) in the main loop to dynamically
#    use these additional parameters for a more nuanced sound simulation.

def get_rpm_from_can_message(msg, target_can_id, byte_index, scale_factor, rpm_offset, debug=False):
    """
    Extracts RPM from a CAN message.

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!! WARNING: CRITICAL USER CONFIGURATION REQUIRED                           !!!
    !!! This function WILL NOT WORK correctly without YOUR specific adjustments !!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    The format of RPM data in a CAN message (its ID, byte order, start byte, number of bytes,
    and any scaling factor) varies *enormously* between vehicle manufacturers and even models.
    You MUST determine the correct parsing logic for YOUR specific vehicle. Failure to do so
    will result in incorrect RPM readings or no readings at all.

    How to determine the correct parsing for your vehicle:
    1. Vehicle Service Manuals: These sometimes contain CAN bus documentation (often in sections
       related to the Engine Control Module (ECM) or Powertrain Control Module (PCM)).
    2. Online Automotive Forums: Search for your car model + "CAN bus RPM format",
       "CAN bus PIDs", or "OBD2 PIDs" (if your CAN bus uses OBD2-like messaging).
    3. CAN Sniffing Tools: This is often the most practical approach.
        - Use a CAN interface (like the PiCAN HAT) and software (`candump` on Linux, or other
          CAN analysis tools) to log CAN messages from your vehicle while the engine is running
          and you (safely) vary the RPM.
        - Look for messages (by CAN ID) whose data changes in sync with the engine's RPM.
        - Once you identify a candidate CAN ID (set via `--rpm-can-id`), you then need to
          decode the data bytes within that message. Note the byte(s) that change, their order
          (endianness), and how the raw value relates to the actual RPM (scaling).
          This will inform your settings for `--rpm-byte-index` and `--rpm-scale-factor`.

    Common RPM Data Formats (Examples - Yours May Differ!):
    - Typically 1 or 2 bytes (8-bit or 16-bit integer).
    - Byte Order (for 2-byte values): Little Endian (less significant byte first) or Big Endian.
    - Scaling: The raw integer value from the CAN message often needs to be multiplied or divided
      by a specific factor to get the true RPM (e.g., value / 4, value * 0.25, value * 1).

    Args:
        msg: The received CAN message object from the `python-can` library.
        target_can_id: The CAN ID (integer) expected for RPM data (from `--rpm-can-id`).
        byte_index: The starting byte index in `msg.data` for RPM data (from `--rpm-byte-index`).
        scale_factor: Factor to multiply the raw CAN value by to get RPM (from `--rpm-scale-factor`).
        rpm_offset: Offset to add to the RPM after scaling (from --rpm-offset).
        debug: Boolean to enable debug prints.

    Returns:
        Calculated RPM as a float, or None if parsing fails, ID doesn't match, or data is insufficient.
    """
    if msg.arbitration_id == target_can_id:
        try:
            # --- START OF USER-CONFIGURABLE SECTION ---
            # The following lines are an EXAMPLE and will likely need to be changed based on your vehicle.
            # This example assumes RPM is a 16-bit little-endian value.

            required_bytes = 2  # How many bytes make up the RPM value (e.g., 2 for 16-bit, 1 for 8-bit)

            if len(msg.data) >= byte_index + required_bytes:
                # Example for 16-bit Little Endian (Intel byte order):
                raw_rpm_value = int.from_bytes(msg.data[byte_index : byte_index + required_bytes], byteorder='little')

                # Example for 16-bit Big Endian (Motorola byte order):
                # raw_rpm_value = int.from_bytes(msg.data[byte_index : byte_index + required_bytes], byteorder='big')

                # Example for an 8-bit (1-byte) RPM value (byte_index would point to this single byte):
                # required_bytes = 1
                # if len(msg.data) >= byte_index + required_bytes:
                #    raw_rpm_value = msg.data[byte_index]
                # else:
                #    if debug: print(f"Debug: Not enough data for 8-bit RPM at index {byte_index}. Data: {msg.data.hex()}")
                #    return None
            # --- END OF USER-CONFIGURABLE SECTION ---
            elif len(msg.data) >= byte_index + 1: # Fallback example if only 1 byte is available (less likely for standard RPM)
                     if debug:
                        print(f"Debug: WARNING - Only {len(msg.data)} bytes available but {required_bytes} needed starting at index {byte_index}. Trying to use 1 byte if possible. Check CAN data format. Data: {msg.data.hex()}")
                     raw_rpm_value = msg.data[byte_index] # Treat the single byte as the raw value, user might need to adjust logic
                else:
                    if debug:
                        print(f"Debug: Not enough data in CAN message for RPM at index {byte_index}. Data: {msg.data.hex()}")
                    return None

                rpm = (raw_rpm_value * scale_factor) + rpm_offset # Apply offset
                if debug:
                    print(f"Debug: Received CAN message. ID: {hex(msg.arbitration_id)}, Data: {msg.data.hex()}, Raw RPM Val: {raw_rpm_value}, Scaled RPM: {rpm:.2f}")
                return rpm
            else:
                if debug:
                    print(f"Debug: RPM byte index {byte_index} (+ {required_bytes-1}) out of range for CAN message data (len: {len(msg.data)}): {msg.data.hex()}")
                return None
        except Exception as e:
            if debug:
                print(f"Debug: Error parsing RPM from CAN message: {e}")
            return None
    return None


# --- Main Program ---
if __name__ == "__main__":
    args = parse_arguments()
    can_bus = None # Initialize can_bus to None

    if args.debug:
        print("Debug mode enabled.")
        print(f"Initial arguments: {args}")

    # Load audio files
    audio_files = load_audio_files(args.audio_path, args.debug)
    if not audio_files:
        print(f"No audio files loaded from '{args.audio_path}'. Ensure path is correct and WAV files exist (e.g., 1000rpm.wav).")
        print("Exiting due to missing audio files.")
        sys.exit(1)
    if args.debug:
        print(f"Loaded audio files for RPMs: {list(audio_files.keys())}")

    # Initialize PyAudio and Audio Stream
    p_audio_instance = pyaudio.PyAudio() # Use the new global name
    audio_stream = None # Use the new global name
    output_device_index = args.audio_device_index # From argparse

    if not args.no_audio: # Only initialize audio if not disabled
        try:
            if output_device_index is None:
                print("No audio device index specified. Attempting to find I2S DAC or suitable output...")
                found_dac = False
                for i in range(p_audio_instance.get_device_count()):
                    dev_info = p_audio_instance.get_device_info_by_index(i)
                    dev_name = dev_info.get('name', '').lower()
                    if args.debug: # More verbose device checking in debug mode
                        print(f"  Checking output device {i}: {dev_info.get('name')} (Max Output: {dev_info.get('maxOutputChannels')})")
                    if dev_info.get('maxOutputChannels', 0) > 0: # Must be an output device
                        # Keywords to identify common DACs or desired outputs on Raspberry Pi
                        if any(keyword in dev_name for keyword in ['dac', 'hifiberry', 'i2s', 'snd_rpi_hifiberry_dac', 'speaker', 'audioinjector', 'allo piano']):
                            output_device_index = i
                            print(f"Found potential DAC/Output: '{p_audio_instance.get_device_info_by_index(i).get('name')}' at index {i}. Using this device.")
                            found_dac = True
                            break
                if not found_dac:
                    print("Could not automatically find a suitable DAC/I2S audio output device.")
                    print("Please check 'aplay -l' and your /boot/config.txt for dtoverlay settings.")
                    print("You may need to specify the device index manually using --audio-device-index.")
                    print("Available output devices:")
                    for i in range(p_audio_instance.get_device_count()):
                        dev_info = p_audio_instance.get_device_info_by_index(i)
                        if dev_info.get('maxOutputChannels', 0) > 0:
                            print(f"  Index {i}: {dev_info.get('name')} (Max Output Channels: {dev_info.get('maxOutputChannels')})")

                    # Fallback to default output device if no DAC auto-detected and no specific index provided
                    try:
                        default_output_device_info = p_audio_instance.get_default_output_device_info()
                        output_device_index = default_output_device_info['index']
                        print(f"Falling back to default output device: '{default_output_device_info['name']}' at index {output_device_index}.")
                    except IOError as e:
                        print(f"Could not get default output device: {e}. Audio output will be disabled.")
                        args.no_audio = True # Disable audio if default device also fails

            if not args.no_audio and output_device_index is not None:
                device_info = p_audio_instance.get_device_info_by_index(output_device_index)
                print(f"Attempting to open audio stream on device index {output_device_index} ('{device_info.get('name')}')")
                print(f"  Using Sample Rate: {args.audio_sample_rate}, Channels: {args.audio_channels}, Chunk Size: {args.audio_chunk_size}")

                audio_stream = p_audio_instance.open(
                    format=pyaudio.paInt16, # Standard format
                    channels=args.audio_channels,
                    rate=args.audio_sample_rate,
                    output=True,
                    output_device_index=output_device_index,
                    frames_per_buffer=args.audio_chunk_size
                )
                print(f"Audio stream opened successfully on device index {output_device_index} ('{device_info.get('name')}').")

        except Exception as e:
            print(f"ERROR: Could not initialize PyAudio or open audio stream: {e}")
            print("  Please check:")
            print("  1. Is an I²S DAC (e.g., HiFiBerry, Adafruit I2S Amp) or other audio output connected and configured?")
            print("  2. Is the correct dtoverlay loaded in /boot/config.txt (e.g., dtoverlay=hifiberry-dac)? Reboot after changes.")
            print("  3. Verify the DAC with 'aplay -l' and ensure the correct --audio-device-index is used if auto-detection fails.")
            print("  4. Ensure 'libasound2-dev' is installed (`sudo apt-get install libasound2-dev`) and PyAudio is correctly installed for your Python version.")
            print("  Audio output will be disabled due to this error.")
            args.no_audio = True
            if audio_stream: # Should be None here, but just in case
                audio_stream.close()
            if p_audio_instance:
                p_audio_instance.terminate()
            p_audio_instance = None # Ensure it's None so cleanup doesn't try to terminate again
            audio_stream = None
    else:
        print("Audio output is disabled via --no-audio argument or due to previous error.")
        p_audio_instance = None # Ensure these are None if audio is disabled from the start
        audio_stream = None

    # Initialize CAN bus
    # Parameters from argparse
    can_interface_name = args.can_interface
    # Ensure rpm_can_id is integer. Argparse lambda already handles hex/dec.
    rpm_can_id = args.rpm_can_id
    rpm_byte_index = args.rpm_byte_index
    rpm_scale_factor = args.rpm_scale_factor
    rpm_offset = args.rpm_offset # New argument

    if not args.test_mode: # Only initialize CAN if not in test mode
        try:
            print(f"Attempting to bring up CAN interface {can_interface_name} at {args.can_bitrate} bps...")
            # Note: Using 'sudo' directly in script is generally discouraged for security reasons.
            # Consider if the user should run the script with sudo, or configure /etc/sudoers.d/
            # or run these ip link commands manually before starting.
            # For simplicity in this example, we'll proceed with sudo in shell command.
            subprocess.run(f"sudo ip link set {can_interface_name} down", shell=True, check=False) # Bring it down first
            subprocess.run(f"sudo ip link set {can_interface_name} up type can bitrate {args.can_bitrate}", shell=True, check=True)
            if args.debug:
                print(f"Debug: CAN interface {can_interface_name} brought up at {args.can_bitrate} bps via ip link.")

            # Define filters for the CAN bus.
            # The CAN filter is set up to match the specific rpm_can_id.
            # This logic infers if the ID is standard (11-bit) or extended (29-bit)
            # based on whether it's numerically larger than the max standard ID (0x7FF).
            # The mask is then set to match the ID exactly.
            # User must ensure `rpm_can_id` is correctly specified.
            is_extended_id = rpm_can_id > 0x7FF
            can_filters = [{
                "can_id": rpm_can_id,
                "can_mask": 0x1FFFFFFF if is_extended_id else 0x7FF, # Exact match mask
                "extended": is_extended_id
            }]
            if args.debug:
                print(f"Debug: Determined CAN ID type: {'Extended (29-bit)' if is_extended_id else 'Standard (11-bit)'}. Filter: {can_filters}")
            # To disable filtering and receive all messages (for debugging, not recommended for production):
            # can_filters = None

            can_bus = can.interface.Bus(channel=can_interface_name, bustype='socketcan', receive_own_messages=False, can_filters=can_filters)
            print(f"Successfully initialized CAN bus on channel '{can_interface_name}' with filters: {can_filters}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to bring up CAN interface '{can_interface_name}' using 'ip link' command: {e}")
            print("  Please ensure 'ip' command is available and you have necessary permissions (e.g., run with sudo).")
            print("  Alternatively, bring up the interface manually: `sudo ip link set can0 up type can bitrate YOUR_BITRATE`")
            print("  Falling back to Test Mode due to CAN interface setup failure.")
            args.test_mode = True # Fallback to test mode
        except can.CanError as e:
            print(f"ERROR: Failed to initialize python-can bus on channel '{can_interface_name}': {e}")
            print("  Please check:")
            print("  1. Is the PiCAN HAT (or other CAN interface) connected correctly?")
            print("  2. Is the SPI interface enabled and mcp2515 overlay configured in /boot/config.txt (for PiCAN)?")
            print(f"  3. Is the '{can_interface_name}' interface already up and configured with the correct bitrate ({args.can_bitrate} bps)?")
            print("     (You might need to run `sudo ip link set can0 up type can bitrate ...` manually if subprocess failed or permissions are insufficient)")
            print("  Falling back to Test Mode due to python-can initialization failure.")
            args.test_mode = True # Fallback to test mode
        except Exception as e: # Catch any other unexpected errors during CAN init
            print(f"ERROR: An unexpected error occurred during CAN bus initialization: {e}")
            print("  Falling back to Test Mode.")
            args.test_mode = True

    if args.test_mode:
        print("--- RUNNING IN TEST MODE ---")
        print("Live CAN bus interaction is disabled. RPM will be simulated or use fixed values if implemented.")
        # You might want to add logic here to simulate RPM changes for testing audio.
        # For now, it will just mean no RPM is read from CAN.

    if not args.test_mode and can_bus:
        print(f"Listening for CAN messages on '{can_interface_name}' for RPM ID {hex(rpm_can_id)}...")
    elif not args.test_mode and not can_bus:
        print(f"ERROR: CAN bus not available and not in test mode. This should not happen if fallback logic is correct. Exiting.")
        # Cleanup audio before exiting (use new global names)
        if 'audio_stream' in locals() and audio_stream and audio_stream.is_active(): audio_stream.stop_stream(); audio_stream.close()
        if 'p_audio_instance' in locals() and p_audio_instance: p_audio_instance.terminate()
        sys.exit(1)

    # Application start message
    if args.test_mode:
        print("DMuffler application started in Test Mode. Press Ctrl+C to exit.")
    else:
        print("DMuffler application started. Press Ctrl+C to exit.")

    print(f"Configured Min RPM: {args.min_rpm}, Max RPM: {args.max_rpm}, Loop Delay: {args.loop_delay}s")
    # audio_files is the map of RPM integer to filepath string
    if args.debug or not audio_files: # Print if debug or if it's empty (which is an issue)
        print(f"Audio files map (RPM:filepath): {audio_files}")
    elif len(audio_files) > 5: # Print summary if many files
        print(f"Audio files map contains {len(audio_files)} entries from RPM {min(audio_files.keys())} to {max(audio_files.keys())}.")
    else: # Print moderately sized maps fully
        print(f"Audio files map (RPM:filepath): {audio_files}")

    print("Press Ctrl+C to stop the application.") # Duplicates the earlier one slightly, but good reminder here.

    current_rpm = 0
    last_played_audio_file = None
    # currently_playing_sound_process = None # For subprocess-based non-blocking audio
    # Initialize current_sim_rpm for test mode's random walk
    current_sim_rpm = args.min_rpm
    rpm_sim_direction = 1

    try:
        while True:
            # --- RPM Acquisition ---
            if args.test_mode:
                # Simulate RPM changes for testing audio transitions
                if rpm_sim_direction == 1:
                    current_sim_rpm += random.randint(20, 100) # Increment by a random amount
                    if current_sim_rpm > args.max_rpm:
                        current_sim_rpm = args.max_rpm
                        rpm_sim_direction = -1
                else:
                    current_sim_rpm -= random.randint(20, 100) # Decrement by a random amount
                    if current_sim_rpm < args.min_rpm:
                        current_sim_rpm = args.min_rpm
                        rpm_sim_direction = 1
                current_rpm = current_sim_rpm
                if args.debug:
                    print(f"[Test Mode] Simulated RPM: {current_rpm:.0f}")

            elif can_bus: # Live CAN bus operation
                try:
                    msg = can_bus.recv(timeout=0.05) # Shorter timeout for responsiveness
                    if msg:
                        rpm_value = get_rpm_from_can_message(msg, rpm_can_id, rpm_byte_index, rpm_scale_factor, rpm_offset, args.debug)
                        if rpm_value is not None:
                            current_rpm = rpm_value
                            # Debug printing for live RPM is now inside get_rpm_from_can_message
                        # else: No valid RPM message, current_rpm holds its value
                    # else: No message received in this cycle, current_rpm holds

                except can.CanError as e:
                    print(f"CAN receive error: {e}. Attempting to continue.")
                    # Consider re-initializing CAN bus or other recovery here if errors persist
                    time.sleep(1) # Avoid spamming errors
                    continue # Skip to next iteration, hoping bus recovers
            else:
                # Should not happen if startup logic is correct (either CAN active or test_mode)
                print("ERROR: No CAN bus and not in Test Mode. Halting.")
                break

            # --- Audio Logic ---
            if not args.no_audio and p_audio_instance:
                # Select audio file based on current RPM
                # The get_audio_file_for_rpm function needs access to audio_files map
                # It seems audio_files is global, so it should be fine.
                # Ensure rpm_thresholds_map is correctly derived if that's what get_audio_file_for_rpm expects
                # The current get_audio_file_for_rpm uses args.audio_path directly, which means audio_files should be used.
                target_audio_file = get_audio_file_for_rpm(current_rpm, audio_files, args.min_rpm, args.max_rpm, args.debug)

                if target_audio_file:
                    # Only start a new thread if the target sound file has changed
                    # AND (no thread is currently running OR the running thread is for a different file - though this latter check is implicit)
                    if target_audio_file != last_played_audio_file:
                        if audio_playback_thread and audio_playback_thread.is_alive():
                            if args.debug:
                                print(f"[MainLoop] RPM change: Target '{target_audio_file}' differs from last '{last_played_audio_file}'. Old thread for {last_played_audio_file} will be replaced.")
                            # Signal the old thread to stop by setting audio_playback_thread to None (or new thread).
                            # The old thread checks this global to see if it should continue.
                            # This is a cooperative way to stop the old thread.
                            # For a more forceful stop, other mechanisms would be needed (e.g. events).
                            # Let's assume for now setting it to None is enough for the old thread to stop writing frames.
                            # The old thread will then clean itself up.
                            # audio_playback_thread = None # Let old thread know it's no longer primary
                            # time.sleep(0.01) # Give a tiny moment for old thread to see the change (optional)

                        if args.debug:
                            print(f"[MainLoop] RPM: {current_rpm:.0f}. Target audio: '{target_audio_file}'. Starting new audio thread.")

                        # Create and start the new audio playback thread
                        # The old audio_playback_thread (if any) will see its reference changed and should stop.
                        new_thread = threading.Thread(
                            target=play_audio_segment_threaded,
                            args=(
                                target_audio_file,
                                p_audio_instance,
                                args.audio_chunk_size,
                                args.debug # Pass debug flag to thread
                            ),
                            daemon=True, # Daemon threads exit when the main program exits
                            name=f"AudioPlayerThread-{os.path.basename(target_audio_file)}"
                        )
                        audio_playback_thread = new_thread # Assign new thread as the current one
                        new_thread.start() # Start the new thread
                        last_played_audio_file = target_audio_file

                    # If the same audio file is targeted, and no thread is alive for it,
                    # this implies the sound finished and should be replayed (if looping desired).
                    # Current play_audio_segment_threaded plays once. For looping, it would need changes,
                    # or we'd restart the thread here. For one-shot sounds, do nothing if file is same.
                    elif not (audio_playback_thread and audio_playback_thread.is_alive()) and args.debug:
                         # This case means: target is same as last, but nothing is playing.
                         # Optional: print(f"[MainLoop] Target '{target_audio_file}' still current, but no thread active. (Not restarting for one-shot sounds)")
                         pass


                elif last_played_audio_file: # Current RPM dictates no sound, but a sound was playing
                    if args.debug:
                        print(f"[MainLoop] RPM {current_rpm:.0f} dictates no audio. Last sound: '{last_played_audio_file}'. (Thread will stop if it sees 'audio_playback_thread' change).")
                    # If audio_playback_thread is this last_played_audio_file's thread, setting it to None signals it to stop.
                    # audio_playback_thread = None # Signal current thread to stop
                    last_played_audio_file = None # Reset, so next valid RPM can trigger a new sound.

            time.sleep(args.loop_delay)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Cleaning up...")
    # Specific errors like can.CanError or pyaudio.PyAudioError within the loop
    # should be handled inside the loop if they are recoverable.
    # Unrecoverable ones or those outside the loop will lead to finally.
    finally:
        global audio_playback_thread # Ensure access to the global for modification

        print("Cleaning up resources...")

        # 1. Signal and wait for audio playback thread to finish
        active_thread_to_join = None
        # Check if audio_playback_thread exists (could be None if never started) and is alive
        # Note: audio_playback_thread is global, so direct access is fine here.
        if audio_playback_thread and audio_playback_thread.is_alive():
            print("Signaling audio thread to stop...")
            active_thread_to_join = audio_playback_thread
            # Signal for the thread's loop condition. The thread checks:
            # `if audio_playback_thread != current_thread_obj:`
            # So, setting it to None makes that condition true for the running thread if it was `current_thread_obj`.
            audio_playback_thread = None

        if active_thread_to_join:
            thread_name = active_thread_to_join.name
            print(f"Waiting for {thread_name} to complete...")
            active_thread_to_join.join(timeout=1.0) # Wait a bit (e.g., 1.0 second)
            if active_thread_to_join.is_alive():
                print(f"{thread_name} did not complete in time.")
            else:
                print(f"{thread_name} completed.")
        else:
            print("No active audio playback thread, or it already completed.")

        # 2. Clean up main PyAudio stream (if it was used globally and is distinct from threaded streams)
        # 'audio_stream' is defined in the main execution scope.
        if 'audio_stream' in locals() and audio_stream:
            try:
                if audio_stream.is_active(): # Check if it's a valid, active stream object
                    audio_stream.stop_stream()
                    audio_stream.close()
                    print("Main shared audio stream (if used) stopped and closed.")
            except Exception as e:
                print(f"Error closing main shared audio stream: {e}")

        # 3. Terminate PyAudio instance (must be after all streams are closed)
        # 'p_audio_instance' is defined in the main execution scope.
        if 'p_audio_instance' in locals() and p_audio_instance:
            try:
                p_audio_instance.terminate()
                print("PyAudio instance terminated.")
            except Exception as e:
                print(f"Error terminating PyAudio instance: {e}")

        # 4. Shutdown CAN bus
        # 'can_bus' is defined in the main execution scope.
        if 'can_bus' in locals() and can_bus:
            try:
                can_bus.shutdown()
                print("CAN bus shutdown.")
            except Exception as e:
                print(f"Error shutting down CAN bus: {e}")

        print("DMuffler application exited.")
