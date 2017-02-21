# Sun-Lite

## Flashing

The flash.sh script can be used to upload firmware to the ESP8266. It will copy all the files in the current directory with the ".py" extension to the board's memory. It also removes all comments and empty lines from these files before uploading to space memory space.

Usage:

./flash.sh [SERIAL PORT]

Example usage:
./flash.sh /dev/ttyUSB0

## Files

- docs/ : Library documents
- user/mosquitto.py : User functions to send commands to the device via MQTT
- flash.sh : Used to upload code to the ESP8266
- main.py : Top level file implementing sensors and outputs
- mqtt.py : Class used to interface with MQTT broker
- sssd1306.py : Screen library
- TCS34725Lib.py : Colour sensor library
- TLS2561Lib.py : Lux sensor library

## Mosquttio User Functions

Two user functions that send data across MQTT to trigger device events.

To use: run user/mosquitto.py with python and call the functions according to needs. Requires paho-mqtt.

1. pip install paho-mqtt
2. python user/mosquitto.py
3. Call function ChangeAlarmTime or TurnOffAlarm

### ChangeAlarmTime(hour,minute)

Change the alarm deadline to _hour_ and _minute_. The alarm will turn on at latest by this time.

### TurnOffAlarm()

Turn off the alarm (whether started by light readings or time comparison).
