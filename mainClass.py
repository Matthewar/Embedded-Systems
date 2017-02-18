from machine import I2C, Pin, PWM, RTC
import ssd1306
import time
import machine
import json

from mqtt import *
from TSL2561Lib import *
#from TCS34725Lib import *

# Usage:
# from mainClass import *
# m = main()
# m.mainLoop()

# Done
def convTime(RFC):
    #"1985-04-12T23:20:50.52Z"
    year = int(RFC[0:4])
    month = int(RFC[5:7])
    day = int(RFC[8:10])
    hours = int(RFC[11:13])
    minutes = int(RFC[14:16])
    seconds = int(RFC[17:19])
    return year,month,day,hours,minutes,seconds

class main:
    def __init__(self):
        self.initMQTT()
        self.initRTC()
        self.initLED()
        self.initI2C()
        self.initSensors()
        self.initOLED()
        self.initBuzzer()

    # Done
    def initMQTT(self):
        self.mqtt = MQTT(self.callbackMQTT)

    def initRTC(self):
        self.rtc = machine.RTC()

    # Done
    def updateTime(self, timeString):
        # Extract time from string
        ext_dattim = convTime(timeString)
        rtc.datetime((ext_dattim[0], ext_dattim[1], ext_dattim[2], 1, ext_dattim[3], ext_dattim[4],     ext_dattim[5]))

    # Done
    def callbackMQTT(self, topic, data):
        data_dict = json.loads(data)
        print(data_dict)
        if topic == "esys\\time":
            jsonTimeString = data_dict['time']
            timeString = self.convTime(jsonTimeString)
            self.updateTime(timeString)
        elif topic == "esys/tbd/command":
            if data_dict['command'] == "time":
                self.alarmHour = int(data_dict['hour'])
                self.alarmMin = int(data_dict['min'])
                # Setup timer interrupt
                # Create date time tuple - use current date and check if the time has passed already.
                #self.rtc.alarm(self.rtc.ALARM0, (self.alarmYear, self.alarmMonth, self.alarmDay, 1,     self.alarmHour, self.alarmMin, 0))
                #self.alarmOn()
            elif data_dict['command'] == "alarm":
                # Alarm off
                self.alertsOff()

    def checkAlarm(self):
        if (self.alarmHour == self.rtc.datetime()[4] and self.alarmMin == self.rtc.datetime()[5]):
            self.alarmOn()

    # Done
    def initLED(self):
        self.pwmLEDr = machine.PWM(Pin(14))
        self.pwmLEDg = machine.PWM(Pin(12))
        self.pwmLEDb = machine.PWM(Pin(13))
        self.pwmLEDr.freq(9000)
        self.pwmLEDg.freq(9000)
        self.pwmLEDb.freq(9000)
        self.pwmLEDr.duty(1023)
        self.pwmLEDg.duty(1023)
        self.pwmLEDb.duty(1023)

    # Done
    def initI2C(self):
        self.i2c = I2C(-1, Pin(5), Pin(4))

    # Done
    def initSensors(self):
        self.lux = TSL2561Lib(self.i2c)
        self.lux.PowerOn()
        #self.col = TCS34725Lib(self.i2c)
        #self.col.PowerOn()
        #self.col.EnableRGBC()
        # Setup interrupts and thresholds
        self.lux.SetIntrThreshold(0, 13000)
        self.lux.SetIntrCtrlSel("LVL")
        self.p2 = Pin(2, Pin.IN)
        self.p2.irq(trigger=Pin.IRQ_FALLING, handler=self.lightRamp)
        #self.rtc.irq(trigger=RTC.ALARM0, handler=self.alarmOn, wake=machine.IDLE)

    # Done
    def initOLED(self):
        self.oled_reset = Pin(15, Pin.OUT, None)
        self.oled_reset.value(0)
        time.sleep_ms(200)
        self.oled_reset.value(1)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c, 0x3D)

    # Done
    def lightRamp(self,p): # Gradually increase light level
        self.pwmLEDr.duty(0)
        self.pwmLEDg.duty(0)
        self.pwmLEDb.duty(0)

    # Done
    def alarmOn(self):
        self.buzz.duty(512)
        # LED on stuff
        self.pwmLEDr.duty(0)
        self.pwmLEDg.duty(0)
        self.pwmLEDb.duty(0)

    # Done
    def alertsOff(self): # Turn off all alerts regardless of light/time trigger.
        self.buzz.duty(0)
        # self.rtc.cancel() FIX!!!!!!!!!!!
        # LED off stuff
        self.pwmLEDr.duty(1023)
        self.pwmLEDg.duty(1023)
        self.pwmLEDb.duty(1023)

    # Done
    def initBuzzer(self):
        self.buzz = PWM(Pin(2))
        self.buzz.freq(440)
        self.buzz.duty(0)

    # TODO - Loop forever
    def mainLoop(self):
        self.mqtt.CheckMsg()
        self.writeTime()
        self.mqtt.SendData(self.lux.GetLux(),0)
        self.checkAlarm()
        time.sleep(1)

    # Done
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

# thinkspeak
#m=main()

#while True:
#    m.mainLoop()
