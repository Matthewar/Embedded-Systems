import ssd1306 #Screen library
import time #Used for delays
import machine #Used for accessing ESP8266 hardware
import json #Converting to/from JSON strings
import mqtt #Broker control class
import TSL2561Lib #Light sensor class
import TCS34725Lib #Colour sensor class

#Function called when MQTT message is recieved
def callbackMQTT(topic, data):
    #Interpret JSON data from MQTT topics
    data_dict = json.loads(data)
    #Check topic that caused callback
    if topic == b'esys/time':
        #Get date string from "date" field
        jsonTimeString = data_dict['date']
        #Update internal timer (RTC) with time
        m.updateTime(jsonTimeString)
    elif topic == b'esys/tbd/command':
        #Get JSON string from "command" field and check command type
        if data_dict['command'] == "time":
            #Set internal alarm time
            m.alarmHour = int(data_dict['hour'])
            m.alarmMin = int(data_dict['min'])
        elif data_dict['command'] == "alarm":
            #Turn off alarm
            m.alertsOff()

class main:
    def __init__(self):
        #Startup system
        self.initMQTT()
        self.initRTC()
        self.initLED()
        self.initI2C()
        self.initSensors()
        self.initOLED()
        #Current lighting level
        self.lightCount = 0
        #Check if alarm is currently on
        self.alarmCurrent = False
        #Current alarm time
        self.alarmHour = None
        self.alarmMin = None

    #MQTT broker (send callback function for recieving messages)
    def initMQTT(self):
        self.mqtt = mqtt.MQTT(callbackMQTT)

    #Realtime clock
    def initRTC(self):
        self.rtc = machine.RTC()

    #Update internal clock with time string (in RFC3339 format)
    def updateTime(self,timeString):
        #Extract time from string
        ext_dattim = self.convTime(timeString)
        #Insert time into real time clock
        self.rtc.datetime((ext_dattim[0], ext_dattim[1], ext_dattim[2], 1, ext_dattim[3], ext_dattim[4], ext_dattim[5], 0))

    #Check if alarm is on
    def checkAlarm(self):
        #Check if current time is alarm time
        if (self.alarmHour == self.rtc.datetime()[4] and self.alarmMin == self.rtc.datetime()[5]):
            #Turn on alarm
            self.alarmCurrent = True
        elif self.lux.GetLux() > 500: #This check is used because the interrupt code (see initSensors method) isn't triggering the TSL2561 intr
            #Increment alarm
            self.lightRamp()

    #Convert time string (RFC3339 format) to numbers
    def convTime(self,RFC):
        #Example time format: "1985-04-12T23:20:50.52Z"
        year = int(RFC[0:4])
        month = int(RFC[5:7])
        day = int(RFC[8:10])
        hours = int(RFC[11:13])
        minutes = int(RFC[14:16])
        seconds = int(RFC[17:19])
        return year,month,day,hours,minutes,seconds

    #Turn on LED outputs
    def initLED(self):
        #Setup PWM for outputs
        self.pwmLEDr = machine.PWM(machine.Pin(14))
        self.pwmLEDg = machine.PWM(machine.Pin(12))
        self.pwmLEDb = machine.PWM(machine.Pin(13))
        #Set frequency for LEDs
        self.pwmLEDr.freq(9000)
        self.pwmLEDg.freq(9000)
        self.pwmLEDb.freq(9000)
        #Set duty cycle to max (LEDs off)
        self.pwmLEDr.duty(1023)
        self.pwmLEDg.duty(1023)
        self.pwmLEDb.duty(1023)

    #I2C Protocol
    def initI2C(self):
        self.i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))

    #Lux and colour sensors
    def initSensors(self):
        #Active light sensor, turn on
        self.lux = TSL2561Lib.TSL2561Lib(self.i2c)
        self.lux.PowerOn()
        #Active colour sensor, turn on, enable colour detection
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

    #Screen activation
    def initOLED(self):
        #Send reset
        self.oled_reset = machine.Pin(15, machine.Pin.OUT, None)
        self.oled_reset.value(0)
        #Wait for reset to complete
        time.sleep_ms(200)
        #Turn off reset
        self.oled_reset.value(1)
        #Connect screen
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c, 0x3D)

    #Gradually increase light level
    def lightRamp(self):
        if self.lightCount < 1020: #Up to max light value
            self.lightCount += 10 #Increase light level
            self.pwmLEDb.duty(1020-self.lightCount) #Increasing duty cycle

    #Turn alarm on
    def alarmOn(self):
        #Lowest duty cycle (white light on)
        self.pwmLEDr.duty(0)
        self.pwmLEDg.duty(0)
        self.pwmLEDb.duty(0)

    #Turn off all alerts regardless of light/time trigger.
    def alertsOff(self):
        #Highest duty cycle (all light off)
        self.pwmLEDr.duty(1023)
        self.pwmLEDg.duty(1023)
        self.pwmLEDb.duty(1023)
        #Turn off alarm variable
        self.alarmCurrent = False
        #Reset light output level
        self.lightCount = 0

    #Main running loop
    def mainLoop(self):
        #Check MQTT broker for messages
        self.mqtt.CheckMsg()
        #Write time to screen
        self.writeTime()
        #Send data to MQTT broker
        colour_string = "R"+hex(self.col.GetRedDataByte())+"G"+hex(self.col.GetGreenDataByte())+"B"+hex(self.col.GetBlueDataByte())
        self.mqtt.SendData(self.lux.GetLux(),colour_string)
        #Check if alarm is currently running
        self.checkAlarm()
        #If alarm is on, change lighting
        if self.alarmCurrent:
            self.alarmOn()
        #Wait for 1 second
        time.sleep(1)

    #Write current time to the screen
    def writeTime(self):
        #Empty screen
        self.oled.fill(0)
        #Read hours
        hours = str(self.rtc.datetime()[4])
        if len(hours) == 1:
            hours = '0' + hours
        #Read minutes
        mins = str(self.rtc.datetime()[5])
        if len(mins) == 1:
            mins = '0' + mins
        #Read seconds
        secs = str(self.rtc.datetime()[6])
        if len(secs) == 1:
            secs = '0' + secs
        #Write text
        self.oled.text(hours + ':' + mins + ':' + secs, 0, 0)
        #Show written text
        self.oled.show()

#Start class
m = main()

#Run a single loop
def runPart():
    m.mainLoop()

#Run multiple loops forever
def run():
    while True:
        runPart()

#Run the program
run()
