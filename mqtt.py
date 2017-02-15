import machine
import json
from umqtt.simple import MQTTClient

class MQTT:
    def __init__(self):
        client = MQTTClient(machine.unique_id(),'192.168.0.10') #New MQTT instance
        client.connect() #Connect to instance
        #?? Need callback?
        client.subscribe("esys/time") #Time topic subscribed for updating time
        client.subscribe("esys/TBD/command") #Command topic subscribed for setting alarm

    def SendLux(self,lux):
        data = json.dump({'name':'Light','Level':lux}) #Assemble JSON string with lux
        client.publish("esys/TBD/lux",bytes(data,'utf-8')) #Send to client
