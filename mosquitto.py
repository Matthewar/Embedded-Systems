# pip install paho-mqtt
import paho.mqtt.client as paho
client = paho.Client()
client.connect("192.168.0.10")
client.loop_start()
client.publish("esys/tbd/command", "string")
