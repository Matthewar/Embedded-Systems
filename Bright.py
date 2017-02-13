import time
import machine

pLEDr = machine.Pin(15)
pwmLEDr = machine.PWM(pLEDr)
pLEDg = machine.Pin(12)
pwmLEDg = machine.PWM(pLEDg)
pLEDb = machine.Pin(13)
pwmLEDb = machine.PWM(pLEDb)

def rgbchoose(timer, level):
	if(timer == 0):
		pwmLEDr.freq(level)
		pwmLEDr.duty(512)
		pwmLEDg.freq(level)
		pwmLEDg.duty(512)
		pwmLEDb.freq(level)
		pwmLEDb.duty(512)
	else:
		pwmLEDr.freq(0)
		pwmLEDr.duty(512)
		pwmLEDg.freq(0)
		pwmLEDg.duty(512)
		pwmLEDb.freq(level)
		pwmLEDb.duty(512)

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