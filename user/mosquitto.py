# pip install paho-mqtt
import json
import paho.mqtt.client as paho
def ChangeAlarmTime(hour,minute):
    client = paho.Client()
    client.connect("192.168.0.10")
    client.loop_start()
    data = json.dumps({'command':'time','hour':hour,'min':minute})
    client.publish("esys/tbd/command", data)
def TurnOffAlarm():
    client = paho.Client()
    client.connect("192.168.0.10")
    client.loop_start()
    data = json.dumps({'command':'alarm'})
    client.publish("esys/tbd/command", data)
