import machine
import json
from umqtt.simple import MQTTClient
import network

class MQTT:
    def __init__(self,callback_function):
        self.initNetwork()
        self.localClient = MQTTClient(machine.unique_id(), '192.168.0.10') #New MQTT instance (local one)
        self.localClient.connect() #Connect to instance
        self.localClient.set_callback(callback_function) #Callback function for reading from MQTT
        self.localClient.subscribe("esys/time") #Time topic subscribed for updating time
        self.localClient.subscribe("esys/tbd/command") #Command topic subscribed for setting alarm

    def initNetwork(self):
        self.ap_if = network.WLAN(network.AP_IF)
        self.ap_if.active(False)
        self.sta_if = network.WLAN(network.STA_IF)
        if not self.sta_if.isconnected():
            self.sta_if.active(True)
            self.sta_if.connect('EEERover', 'exhibition')
            while not self.sta_if.isconnected():
                pass

    def SendData(self,lux,colour):
        data = json.dumps({'name':'Light','Level':lux,'Colour':colour}) #Assemble JSON string with lux
        self.localClient.publish("esys/tbd/lux",bytes(data,'utf-8')) #Send to client

    def CheckMsg(self):
        self.localClient.check_msg()
