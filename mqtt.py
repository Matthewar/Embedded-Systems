# put this at the end of main.py
import machine
import json
from umqtt.simple import MQTTClient

client = MQTTClient(machine.unique_id(),'192.168.0.10')
client.connect()

client.publish()