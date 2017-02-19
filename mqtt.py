import machine #For device functions
import json #Converting to/from JSON strings
from umqtt.simple import MQTTClient #MQTT client for broker
import network #Network access (wifi)

class MQTT:
    def __init__(self,callback_function):
        self.initNetwork() #Startup internet
        self.localClient = MQTTClient(machine.unique_id(), '192.168.0.10') #New MQTT instance
        self.localClient.connect() #Connect to instance
        self.localClient.set_callback(callback_function) #Callback function for reading from MQTT
        self.localClient.subscribe("esys/time") #Time topic subscribed for updating time
        self.localClient.subscribe("esys/tbd/command") #Command topic subscribed for setting alarm

    #Connect to internet and access point
    def initNetwork(self):
        self.ap_if = network.WLAN(network.AP_IF) #Startup access point
        self.ap_if.active(False) #Disable access point output
        self.sta_if = network.WLAN(network.STA_IF) #Startup station recieving
        if not self.sta_if.isconnected(): #If not connected to station
            self.sta_if.active(True) #Activate station connection
            self.sta_if.connect('EEERover', 'exhibition') #Connect to local station
            while not self.sta_if.isconnected(): #While not connected, wait
                pass

    #Send data to broker
    def SendData(self,lux,colour):
        data = json.dumps({'name':'Light','Level':lux,'Colour':colour}) #Assemble JSON string with lux
        self.localClient.publish("esys/tbd/lux",bytes(data,'utf-8')) #Send to client

    #Check MQTT broker messages
    def CheckMsg(self):
        self.localClient.check_msg()
