from machine import I2C, Pin

#?? Move constants to shared file
SCL_PIN = 5
SDA_PIN = 4
##

#?? Changes required to meet coding naming standards

class SensorLib:
    #Constants
    #- Read Data (bits used for I2C)
    __COMMAND_BIT = 0x80
    __WORD_BIT    = 0x20

    # Dictionaries for used values
    #- Register
    INTERNAL_REGISTER = {
        "CONTROL"        : 0x0,
        "TIMING"         : 0x1,
        "THRESLOWLOW"    : 0x2,
        "THRESLOWHIGH"   : 0x3,
        "THRESHIGHLOW"   : 0x4,
        "THRESHIGHHIGH"  : 0x5,
        "INTERRUPT"      : 0x6,
        "CRC"            : 0x8,
        "ID"             : 0xA,
        "DATA0LOW"       : 0xC,
        "DATA0HIGH"      : 0xD,
        "DATA1LOW"       : 0xE,
        "DATA1HIGH"      : 0xF
    }
    #- Gain Modes
    GAIN_MODE = {
        "X1"    : False,
        "X16"   : True
    }
    #- Possible I2C addresses (depending on connection of ADDR pin)
    SLAVE_ADDRS = {
        "GND"   : 0x29, #0101001/49
        "FLOAT" : 0x39, #0111001/57
        "VDD"   : 0x49  #1001001/73
    }

    def __init__(self,i2c,addr="FLOAT"):
        #Load I2C object passed
        self.i2c = i2c
        #Set Slave Address
        self.__SLAVE_ADDR = SensorLib.SLAVE_ADDRS[addr]
        # Internal State
        self.__deviceOn = True
        self.__regTiming = 0x02 #Timing Register contents ?? Load from device instead of using default

    def __WriteData(self,reg,data):
        self.i2c.writeto_mem(self.__SLAVE_ADDR, reg, data) #?? Check ACKs received and resend if necessary ?? Need to convert Data to bytes

    def __ReadData(self,reg,twoBytes=False):
        reg |= SensorLib.__COMMAND_BIT | SensorLib.__WORD_BIT #Prepare address for device format
        if twoBytes:
            numBytes = 2
        else:
            numBytes = 1
        return self.i2c.readfrom_mem(self.__SLAVE_ADDR, reg, numBytes)[0]

    def PowerUp(self,force=False):
        if not self.__deviceOn or force:
            __WriteData(SensorLib.INTERNAL_REGISTER["CONTROL"],0x03)
            if (self.__ReadData(SensorLib.INTERNAL_REGISTER["CONTROL"]) != 0x03):
                raise Exception("I2C power up failed")
            else:
                self.__deviceOn = True

    def PowerDown(self,force=False):
        if self.__deviceOn or force:
            self.__WriteData(SensorLib.INTERNAL_REGISTER["CONTROL"],0x00)
            if (self.__ReadData(SensorLib.INTERNAL_REGISTER["CONTROL"]) != 0x00):
                raise Exception("I2C power down failed")
            else:
                self.__deviceOn = False

    def SetGainMode(self,mode):
        if mode: #X16 mode
            self.__regTiming |= 0x10 #Write a 1 to bit 4
        else: #X1 mode
            self.__regTiming &= 0xEF #Write a 0 to bit 4
        self.__WriteData(SensorLib.INTERNAL_REGISTER["TIMING"],self.__regTiming)

    def GetGainMode(self):
        return self.__ReadData(SensorLib.INTERNAL_REGISTER["TIMING"]) & 0x10 #Get bit 4 of TIMING reg

    #def ChangeTiming(self,timingSetting): ?? Todo

    def SetIntrpThreshold(self,low,high):
        if low is not None:
            if low > 255 or low < 0:
                raise Exception("Low value out of bounds")
            else:
                __WriteData(SensorLib.INTERNAL_REGISTER["THRESLOWHIGH"],low.to_bytes(2,'little')[15:8])
                __WriteData(SensorLib.INTERNAL_REGISTER["THRESLOWLOW"],low.to_bytes(2,'little')[7:0])
        if high is not None:
            if high > 255 or high < 0:
                raise Exception("High value out of bounds")
            else:
                __WriteData(SensorLib.INTERNAL_REGISTER["THRESHIGHHIGH"],high.to_bytes(2,'little')[15:8])
                __WriteData(SensorLib.INTERNAL_REGISTER["THRESHIGHLOW"],high.to_bytes(2,'little')[7:0])

    def GetIntrpLowThreshold(self):
        lowThreshold        = bytearray(2)
        lowThreshold[0]   = self.__ReadData(SensorLib.INTERNAL_REGISTER["THRESLOWLOW"])
        lowThreshold[1]  = self.__ReadData(SensorLib.INTERNAL_REGISTER["THRESLOWHIGH"])
        return lowThreshold

    def GetIntrpHighThreshold(self):
        highThreshold        = bytearray(2)
        highThreshold[0]    = self.__ReadData(SensorLib.INTERNAL_REGISTER["THRESHIGHLOW"])
        highThreshold[1]    = self.__ReadData(SensorLib.INTERNAL_REGISTER["THRESHIGHHIGH"])
        return highThreshold

    #Interrupt control changing function here
    def GetPartNumber(self):
        return self.__ReadData(SensorLib.INTERNAL_REGISTER["ID"])[7:4]

    def GetRevNumber(self):
        return self.__ReadData(SensorLib.INTERNAL_REGISTER["ID"])[3:0]

    def ReadADC0(self): #Visible and IR
        data    = bytearray(2)
        data[0] = int(self.__ReadData(SensorLib.INTERNAL_REGISTER["DATA0LOW"]))
        data[1] = int(self.__ReadData(SensorLib.INTERNAL_REGISTER["DATA0HIGH"]))
        return data

    def ReadADC1(self): #Just IR
        data    = bytearray(2)
        data[0] = self.__ReadData(SensorLib.INTERNAL_REGISTER["DATA1LOW"])
        data[1] = self.__ReadData(SensorLib.INTERNAL_REGISTER["DATA1HIGH"])
        return data

#Registers
##ADDR    REG NAME        REG FUNC                                  FORMAT
##--      COMMAND         Specifies register address
##0h      CONTROL         Control of basic functions                Bits 7:2 reserved, write as 0. Bits 1:0 = Power, write 00 for power off, 03h for power on
##1h      TIMING          Integration time/gain control             Bits 7:5 reserved, write as 0. Bit 4 = gain mode (0 = low gain (1x), 1 = high gain (16x)), Bit 3 = manual timing control (1 for begin cycle, 0 for end), Bit 2 reserved, write as 0. Bits 1:0 = Integrate time for conversion (see datasheet)
##2h      THRESLOWLOW     Low byte of low interrupt threshold       Stores values used as trigger points for interrupt generation (two 16 bit threshold values, default 00h)
##3h      THRESLOWHIGH    High byte of low interrupt threshold      "
##4h      THRESHIGHLOW    Low byte of high interrupt threshold      "
##5h      THRESHIGHHIGH   High byte of high interrupt threshold     "
##6h      INTERRUPT       Interrupt control                         Bits 7:6 reserved, write as 0. Bits 5:4 = control select (see datasheet), bits 3:0 = persistence (see datasheet)
##7h      --              Reserved
##8h      CRC             Factory test (not a user register)
##9h      --              Reserved
##Ah      ID              Part number/Rev ID                        READ ONLY, bits 7:4 part no. bits 3:0 revision no.
##Bh      --              Reserved
##Ch      DATA0LOW        Low byte of ADC channel 0                 Data from ADCs. Read lower byte first. NOTE: Channel 0 = Visible and IR, Channel 1 = Just IR
##Dh      DATA0HIGH       High byte of ADC channel 0                "
##Eh      DATA1LOW        Low byte of ADC channel 1                 "
##Fh      DATA1HIGH       High byte of ADC channel 1                "
