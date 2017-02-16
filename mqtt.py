import machine
import json
from umqtt.simple import MQTTClient

class MQTT:
    def __init__(self,callback_function):
        self.client = MQTTClient(machine.unique_id(), '192.168.0.10') #New MQTT instance
        self.client.connect() #Connect to instance
        self.client.set_callback(callback_function)
#        print(self.client.subscribe("esys\\time")) #Time topic subscribed for updating time
#        print(self.client.subscribe("esys/TBD/command")) #Command topic subscribed for setting alarm

    def SendLux(self,lux):
        data = json.dumps({'name':'Light','Level':lux}) #Assemble JSON string with lux
        self.client.publish("esys/TBD/lux",bytes(data,'utf-8')) #Send to client

    def CheckMsg(self):
        self.client.check_msg()

