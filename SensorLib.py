from machine import I2C, Pin

#?? Move constants to shared file
SCL_PIN = 5
SDA_PIN = 4
##

class SensorLib:
    # Dictionaries for used values
    #- Register
    InternalRegister = {
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
    GainMode = {
        "X1"    : False,
        "X16"   : True
    }
    #- Possible I2C addresses (depending on connection of ADDR pin)
    SlaveAddrs = {
        "GND"   : 0x29, #0101001/49
        "FLOAT" : 0x39, #0111001/57
        "VDD"   : 0x49  #1001001/73
    }

    def __init__(self,addr="FLOAT"): #?? Pass I2C to init from master controller (so can use multiple slaves on I2C bus)
        #Initialise I2C class
        self.i2c = I2C(-1, Pin(SCL_PIN), Pin(SDA_PIN))
        #Set Slave Address
        self.__SlaveAddr = SensorLib.SlaveAddrs[addr]
        # Internal State
        self.__DeviceOn = True
        self.__RegTiming = bytearray(0)

    def __WriteData(self,Reg,Data):
        self.i2c.writeto_mem(self.__SlaveAddr, Reg, Data) #?? Check ACKs received and resend if necessary ?? Need to convert Data to bytes

    def __ReadData(self,Reg):
        return self.i2c.readfrom_mem(self.__SlaveAddr, Reg, 1)[0]

    def PowerUp(self,Force=False): #?? Return values for these, include check for success?
        if not self.__DeviceOn or Force:
            __WriteData(SensorLib.InternalRegister["CONTROL"],0x03)
            self.__DeviceOn = True

    def PowerDown(self,Force=False): #?? Return values for these, include check for success?
        if self.__DeviceOn or Force:
            self.__WriteData(SensorLib.InternalRegister["CONTROL"],0x00)
            self.__DeviceOn = False

    def SetGainMode(self,Mode):
        if Mode:
            self.__RegTiming[4] = 1
        else:
            self.__RegTiming[4] = 0
        __WriteData(SensorLib.InternalRegister["TIMING"],self.__RegTiming)

    def GetGainMode(self):
        return self.__ReadData(SensorLib.InternalRegister["TIMING"])[4]

    #def ChangeTiming(TimingSetting): ?? Todo

    def SetIntrpThreshold(Low,High):
        if Low is not None:
            if Low > 255 or Low < 0:
                raise Exception("Low value out of bounds")
            else:
                __WriteData(SensorLib.InternalRegister["THRESLOWHIGH"],Low.to_bytes(2,'little')[15:8])
                __WriteData(SensorLib.InternalRegister["THRESLOWLOW"],Low.to_bytes(2,'little')[7:0])
        if High is not None:
            if High > 255 or High < 0:
                raise Exception("High value out of bounds")
            else:
                __WriteData(SensorLib.InternalRegister["THRESHIGHHIGH"],High.to_bytes(2,'little')[15:8])
                __WriteData(SensorLib.InternalRegister["THRESHIGHLOW"],High.to_bytes(2,'little')[7:0])

    def GetIntrpLowThreshold(self):
        LowThreshold        = bytearray(2)
        LowThreshold[0]   = self.__ReadData(SensorLib.InternalRegister["THRESLOWLOW"])
        LowThreshold[1]  = self.__ReadData(SensorLib.InternalRegister["THRESLOWHIGH"])
        return LowThreshold

    def GetIntrpHighThreshold(self):
        HighThreshold        = bytearray(2)
        HighThreshold[0]    = self.__ReadData(SensorLib.InternalRegister["THRESHIGHLOW"])
        HighThreshold[1]    = self.__ReadData(SensorLib.InternalRegister["THRESHIGHHIGH"])
        return HighThreshold

    #Interrupt control changing function here
    def GetPartNumber(self):
        return self.__ReadData(SensorLib.InternalRegister["ID"])[7:4]

    def GetRevNumber(self):
        return self.__ReadData(SensorLib.InternalRegister["ID"])[3:0]

    def ReadADC0(self): #Visible and IR
        Data    = bytearray(2)
        Data[0] = int(self.__ReadData(SensorLib.InternalRegister["DATA0LOW"]))
        Data[1] = int(self.__ReadData(SensorLib.InternalRegister["DATA0HIGH"]))
        return Data

    def ReadADC1(self): #Just IR
        Data        = bytearray(2)
        Data[0] = self.__ReadData(SensorLib.InternalRegister["DATA1LOW"])
        Data[1] = self.__ReadData(SensorLib.InternalRegister["DATA1HIGH"])
        return Data

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
