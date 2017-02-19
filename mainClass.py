import ssd1306
import time
import machine
import json

from mqtt import MQTT
from TSL2561Lib import *
import TCS34725Lib

# Usage:
# from mainClass import *
# m = main()
# m.mainLoop()

def callbackMQTT(topic, data):
    data_dict = json.loads(data)
    print(data_dict)
    print (topic)
    if topic == b'esys/time':
        jsonTimeString = data_dict['date']
        #timeString = m.convTime(jsonTimeString)
        m.updateTime(jsonTimeString)
    elif topic == b'esys/tbd/command':
        if data_dict['command'] == "time":
            m.alarmHour = int(data_dict['hour'])
            m.alarmMin = int(data_dict['min'])
        elif data_dict['command'] == "alarm":
            # Alarm off
            m.alertsOff()

class main:
    def __init__(self):
        #Startup MQTT system
        self.initMQTT()
        self.initRTC()
        self.initLED()
        self.initI2C()
        self.initSensors()
        self.initOLED()
        self.lightCount = 0
        self.alarmCurrent = False
        self.alarmHour = 0
        self.alarmMin = 0

    #MQTT Client
    def initMQTT(self):
        self.mqtt = MQTT(callbackMQTT)

    def initRTC(self):
        self.rtc = machine.RTC()

    def updateTime(self, timeString):
        # Extract time from string
        ext_dattim = self.convTime(timeString)
        self.rtc.datetime((ext_dattim[0], ext_dattim[1], ext_dattim[2], 1, ext_dattim[3], ext_dattim[4],     ext_dattim[5],0))

    def checkAlarm(self):
        if (self.alarmHour == self.rtc.datetime()[4] and self.alarmMin == self.rtc.datetime()[5]):
            self.alarmCurrent = True
        elif self.lux.GetLux() > 500: #This check is used because the interrupt code (see initSensors method) isn't triggering the TSL2561 intr
            self.lightRamp()

    def convTime(self,RFC):
        #"1985-04-12T23:20:50.52Z"
        year = int(RFC[0:4])
        month = int(RFC[5:7])
        day = int(RFC[8:10])
        hours = int(RFC[11:13])
        minutes = int(RFC[14:16])
        seconds = int(RFC[17:19])
        return year,month,day,hours,minutes,seconds

    def initLED(self):
        self.pwmLEDr = machine.PWM(machine.Pin(14))
        self.pwmLEDg = machine.PWM(machine.Pin(12))
        self.pwmLEDb = machine.PWM(machine.Pin(13))
        self.pwmLEDr.freq(9000)
        self.pwmLEDg.freq(9000)
        self.pwmLEDb.freq(9000)
        self.pwmLEDr.duty(1023)
        self.pwmLEDg.duty(1023)
        self.pwmLEDb.duty(1023)

    def initI2C(self):
        self.i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))

    def initSensors(self):
        self.lux = TSL2561Lib(self.i2c)
        self.lux.PowerOn()
        self.col = TCS34725Lib.TCS34725Lib(self.i2c)
        self.col.PowerOn()
        self.col.EnableRGBC()
####################################################################################################
        #Chip interrupt should work this way but seems to trigger immediately on run instead.
        ## Setup interrupts and thresholds
        #self.lux.SetIntrThreshold(0, 13000)
        #self.lux.SetIntrCtrlSel("LVL")
        #self.p2 = machine.Pin(2, machine.Pin.IN)
        #self.p2.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.lightRamp)
####################################################################################################

    def initOLED(self):
        self.oled_reset = machine.Pin(15, machine.Pin.OUT, None)
        self.oled_reset.value(0)
        time.sleep_ms(200)
        self.oled_reset.value(1)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c, 0x3D)

    def lightRamp(self): # Gradually increase light level
        if self.lightCount < 1020:
            self.lightCount += 10
        #self.pwmLEDr.duty(1025-self.lightCount)
        #self.pwmLEDg.duty(1025-self.lightCount)
        self.pwmLEDb.duty(1020-self.lightCount)

    def alarmOn(self):
        # LED on stuff
        self.pwmLEDr.duty(0)
        self.pwmLEDg.duty(0)
        self.pwmLEDb.duty(0)

    def alertsOff(self): # Turn off all alerts regardless of light/time trigger.
        # LED off stuff
        self.pwmLEDr.duty(1023)
        self.pwmLEDg.duty(1023)
        self.pwmLEDb.duty(1023)
        self.alarmCurrent = False

    def mainLoop(self):
        self.mqtt.CheckMsg()
        self.writeTime()
        colour_string = "R"+hex(self.col.GetRedDataByte())+"G"+hex(self.col.GetGreenDataByte())+"B"+hex(self.col.GetBlueDataByte())
        self.mqtt.SendData(self.lux.GetLux(),colour_string)
        self.checkAlarm()
        if self.alarmCurrent:
            self.alarmOn()
        time.sleep(1)

    def writeTime(self):
        self.oled.fill(0)
        hours = str(self.rtc.datetime()[4])
        if len(hours) == 1:
            hours = '0' + hours
        mins = str(self.rtc.datetime()[5])
        if len(mins) == 1:
            mins = '0' + mins
        secs = str(self.rtc.datetime()[6])
        if len(secs) == 1:
            secs = '0' + secs
        self.oled.text(hours + ':' + mins + ':' + secs, 0, 0)
        self.oled.show()

m = main()

def runPart():
    m.mainLoop()

def run():
    while True:
        runPart()
