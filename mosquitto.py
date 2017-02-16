# pip install paho-mqtt
import paho.mqtt.client as paho
def ChangeAlarmTime(hour,minute):
    client = paho.Client()
    client.connect("192.168.0.10")
    client.loop_start()
    data = json.dumps({'hour':hour,'min':minute})
    client.publish("esys/tbd/command", data)
