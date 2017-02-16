import time
import machine

pLEDr = machine.Pin(15)
pwmLEDr = machine.PWM(pLEDr)
pLEDg = machine.Pin(12)
pwmLEDg = machine.PWM(pLEDg)
pLEDb = machine.Pin(13)
pwmLEDb = machine.PWM(pLEDb)

def rgbchoose(timer, level):
    if(timer == 1):
        pwmLEDr.freq(0)
        pwmLEDr.duty(level)
        pwmLEDg.freq(0)
        pwmLEDg.duty(level)
        pwmLEDb.freq(0)
        pwmLEDb.duty(level)
    else:
        pwmLEDr.freq(1024)
        pwmLEDr.duty(level)
        pwmLEDg.freq(1024)
        pwmLEDg.duty(level)
        pwmLEDb.freq(0)
        pwmLEDb.duty(level)

#timer: accessing if the alarm has triggered. 0 = No. 1 = Yes.
#sun: current level of sun.
#level: last recorded level of sun. Defaults to 0.
def brightness(timer,sun,level):
    if(timer == 0,level == sun):
        print("ON")
    else:
        level = float(0)
        if(timer == 1):
            while level < 5000:
                print(level)
                time.sleep(1)
                level += 100
                rbgchoose(timer,level)
            print("TIMER")
        else:
            level = sun
            print(level)
            print("LIGHT")
            rgbchoose(timer,level)