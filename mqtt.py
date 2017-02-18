import machine
import json
from umqtt.simple import MQTTClient
import network

class MQTT:
    def __init__(self,callback_function):
        self.initNetwork()
        self.connectLocalAP()
        self.localClient = MQTTClient(machine.unique_id(), '192.168.0.10') #New MQTT instance (local one)
        self.localClient.set_callback(callback_function) #Callback function for reading from MQTT
        self.disconnectAP()
        self.connectRemoteAP()
        self.remoteClient = MQTTClient(machine.unique_id(), 'mqtt.thingspeak.com') #New MQTT instance (online one)
        self.disconnectAP()

    def initNetwork(self):
        self.ap_if = network.WLAN(network.AP_IF)
        self.ap_if.active(False)
        self.sta_if = network.WLAN(network.STA_IF)

    def connectLocalAP(self):
        if not self.sta_if.isconnected():
            self.sta_if.active(True)
            self.sta_if.connect('EEERover', 'exhibition')
            while not self.sta_if.isconnected():
                pass

    def connectRemoteAP(self):
        if not self.sta_if.isconnected():
            self.sta_if.active(True)
            self.sta_if.connect('android_hub_tmp', 'eesys_password')
            while not self.sta_if.isconnected():
                pass

    def disconnectAP(self):
        self.sta_if.disconnect()

    def ConnectLocalHost(self):
        self.localClient.connect() #Connect to instance

    def DisconnectLocalHost(self):
        self.localClient.disconnect() #Disconnect

    def ConnectRemoteHost(self):
        self.remoteClient.connect()

    def DisconnectRemoteHost(self):
        self.remoteClient.disconnect() #Disconnect

    def SendLux(self,lux):
        data = json.dumps({'name':'Light','Level':lux}) #Assemble JSON string with lux
        self.ConnectLocalHost()
        self.localClient.publish("esys/TBD/lux",bytes(data,'utf-8')) #Send to client
        self.DisconnectLocalHost()

    def SendRemoteData(self,lux,colour):
        credentials="channels/{:s}/publish/{:s}".format("228193","77S4VPV3GNSU61OI")
        data = "field1={:d}&field2\n={:d}".format(lux,colour)
        self.connectRemoteAP()
        self.ConnectRemoteHost()
        self.remoteClient.publish(credentials,data)
        self.DisconnectRemoteHost()
        self.disconnectAP()

    def SendData(self,lux,colour):
        self.SendLux(lux)
        self.SendRemoteData(lux,colour)

    def CheckMsg(self):
        self.connectLocalAP()
        self.ConnectLocalHost()
        self.client.subscribe("esys\\time") #Time topic subscribed for updating time
        self.client.subscribe("esys/TBD/command") #Command topic subscribed for setting alarm
        #self.localClient.check_msg()
        self.DisconnectLocalHost()
        self.disconnectAP()
