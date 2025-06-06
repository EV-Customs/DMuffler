# DMuffler
Digital muffler for electric and hybrid vehicles


Hardware Required: <br>
1) Hardware Dongle from CANOPi [TesCustoms P/N 100-0001-A](https://github.com/TesCustoms/TesMufflerDongle) <br>
2) Raspberry Pi Compute Module 4 [Pi Foundation P/N CM4](https://www.raspberrypi.com/products/compute-module-4)
3) SeeddStudio Dual Gigabit Carrier Board CM4 Carrier Board [SeedStudio SKU 102110497](https://wiki.seeedstudio.com/Dual-Gigabit-Ethernet-Carrier-Board-for-Raspberry-Pi-CM4/#fpc-interface)
4) OHP OBD2 Adapter Harness [Manufacture P/N 10246](www.amazon.com/dp/B08DXY5KVX/ref=cm_sw_r_cp_api_glt_fabc_M5VV59NMV6AZKJVCRG4D?) <br>
5) Custom 3D CAD file [TesMufflerCADv1.stl](https://github.com/OpenSourceIronman/Tes/blob/master/TesMuffler/TesMufflerCADv1.stl) 3D printed muffler with magnets <br>
<br>

Python APIs project is exploring: <br>
1) Tesla API is a community of developers who are reverse engineering Tesla’s API: https://teslaapi.dev/ <br> 
2) Smartcar API lets you read vehicle data (location, odometer) and send commands to vehicles (lock, unlock) to connected vehicles using HTTP requests: https://github.com/smartcar/python-sdk <br>
3) The Comma Pedal is a gas pedal interceptor. It is a device that is inserted between a car’s electronic gas pedal and the ECU (Engine Control Unit): https://github.com/commaai/openpilot/wiki/comma-pedal <br>
4) All Comma Software: https://github.com/commaai/panda/tree/ad12330d506ca31fe16f99a5b5aca76aab8a1ec9 <br>
5) TODO https://teslascope.com/
<br>

Usage Examples
-------------

### Connect with Retry

The `connect_with_retry` function can be used to establish a connection to a device with retry mechanism. Here is an example usage:

```python
import time

# Attempt to connect to the device with a maximum of 5 retries and a 1-second delay between retries
device = connect_with_retry(max_retries=5, delay=1)

if device:
    print("Connected to the device successfully")
else:
    print("Failed to connect to the device after 5 retries")
```

### Example Pitch Shift

The `example_pitch_shift` function can be used to shift the pitch of an audio signal. Here is an example usage:

```python
import numpy as np

# Generate a sample audio signal
sample_rate = 44100
frequency = 440  # Hz
duration = 1  # second
t = np.linspace(0, duration, int(sample_rate * duration), False)
note = np.sin(frequency * t * 2 * np.pi)

# Shift the pitch of the audio signal by 2 semitones
shifted_note = example_pitch_shift(note, sample_rate, 2)

# Play the shifted audio signal
import sounddevice as sd
sd.play(shifted_note, sample_rate)
sd.wait()
```

Next steps: <br>
Download the following sounds using “youtube-dl —extract-audio —audio-format mp3 http://videoURL” linux command
1) [McLaren F1](www.youtube.com/watch?v=mOI8GWoMF4M) <br>
2) [Ferrari LaFerrari](https://www.youtube.com/watch?v=B4Th3LxCgb4) <br>
3) [Porcshe 911](https://www.youtube.com/watch?v=O1Kyt1qDL30) <br>
4) [BWM M4](https://www.youtube.com/watch?v=0RFoYCG4_TE) <br>
5) [Jaguar E Type Series 1](https://www.youtube.com/watch?v=44sNpPYw5Bo) <br>
6) [Ford Model T](https://www.dailymotion.com/video/x35n5if) <br>
7) [Subaru WRX STI](https://youtu.be/d7Gszyz62e0?t=193) <br>
8) [Motor whine directly from your Tesla](https://www.youtube.com/watch?v=j4AxsGk-LdQ) <br>
9) [Star Wars Pod Racer](https://www.youtube.com/watch?v=f7ogSqLwNQ0) <br>
8) OTHER SUGGESTIONS? Tweet me @BlazeDSanders or submit GitHub issue <br>
<br>

Why?: <br>
1) https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/812347-minimumsoundrequirements.pdf <br>
2) https://www.cnbc.com/2017/10/12/tesla-ceo-elon-musk-reveals-he-owns-two-gasoline-cars.html <br>
<br>


TODO: 
Display for PiPico https://www.hackster.io/news/miroslav-nemecek-s-picovga-brings-high-res-video-to-the-raspberry-pi-pico-just-add-resistors-88dd144e7d1c
FIND URLS I DELETED FROM TOP OF EngineSoundGenerator.py FILE https://whimsical.com/tesmuffler-64NBDWF5cd3stpZDvkubzw
AM Radio IC [Manufacture P/N TODO](https://www.petervis.com/Radios/ta7642/ta7642-am-radio-ic.html)