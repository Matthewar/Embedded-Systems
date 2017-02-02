from machine import I2C, Pin
#from enum import Enum

#?? Move constants to shared file
SCL_PIN = 5
SDA_PIN = 4
##

class SensorLib:
    # Constants
    ## Frequency
    MIN_CLK_FREQ = 0
    MAX_CLK_FREQ = 400000
    ## Slave Addresses
    ### ADDR SEL TERMINAL LEVEL   ADDR
    ### GND                       0101001 = 41
    ### Float                     0111001 = 57
    ### VDD                       1001001 = 73
    SLAVE_ADDR = 57 #?? Add argument to init to choose address ?? convert values to hex

    # Types
    #- Register
    #class InternalRegister(Enum): ?? Change to dictionary for coherency - enums don't exist
    CONTROL         = 0
    TIMING          = 1
    THRESLOWLOW     = 2
    THRESLOWHIGH    = 3
    THRESHIGHLOW    = 4
    THRESHIGHHIGH   = 5
    INTERRUPT       = 6
    CRC             = 8
    ID              = 10
    DATA0LOW        = 12
    DATA0HIGH       = 13
    DATA1LOW        = 14
    DATA1HIGH       = 15
    #class GainMode(Enum):
    X1  = False
    X16 = True

    def __init__(self):
        #Initialise I2C class
        self.i2c = I2C(-1, Pin(SCL_PIN), Pin(SDA_PIN))
        #?? Set address of slave device
        # Internal State
        self.__DeviceOn = True
        self.__RegTiming = bytearray(0)

    def __WriteData(self,Reg,Data):
        self.i2c.writeto_mem(SensorLib.SLAVE_ADDR, Reg, Data) #?? Check ACKs received and resend if necessary ?? Need to convert Data to bytes

    def __ReadData(self,Reg):
        return self.i2c.readfrom_mem(SensorLib.SLAVE_ADDR, Reg, 1)[0]

    def PowerUp(self,Force=False): #?? Return values for these, include check for success?
        if not self.__DeviceOn or Force:
            __WriteData(SensorLib.CONTROL,3)
            self.__DeviceOn = True

    def PowerDown(self,Force=False): #?? Return values for these, include check for success?
        if self.__DeviceOn or Force:
            self.__WriteData(SensorLib.CONTROL,0)
            self.__DeviceOn = False

    def SetGainMode(self,Mode):
        if Mode:
            self.__RegTiming[4] = 1
        else:
            self.__RegTiming[4] = 0
        __WriteData(SensorLib.TIMING,self.__RegTiming)

    def GetGainMode(self):
        return self.__ReadData(SensorLib.TIMING)[4]

    #def ChangeTiming(TimingSetting): ?? Todo

    def SetIntrpThreshold(Low,High):
        if Low is not None:
            if Low > 255 or Low < 0:
                raise Exception("Low value out of bounds")
            else:
                __WriteData(SensorLib.THRESLOWHIGH,Low.to_bytes(2,'little')[15:8])
                __WriteData(SensorLib.THRESLOWLOW,Low.to_bytes(2,'little')[7:0])
        if High is not None:
            if High > 255 or High < 0:
                raise Exception("High value out of bounds")
            else:
                __WriteData(SensorLib.THRESHIGHHIGH,High.to_bytes(2,'little')[15:8])
                __WriteData(SensorLib.THRESHIGHLOW,High.to_bytes(2,'little')[7:0])

    def GetIntrpLowThreshold(self):
        LowThreshold        = bytearray(2)
        LowThreshold[0]   = self.__ReadData(SensorLib.THRESLOWLOW)
        LowThreshold[1]  = self.__ReadData(SensorLib.THRESLOWHIGH)
        return LowThreshold

    def GetIntrpHighThreshold(self):
        HighThreshold        = bytearray(2)
        HighThreshold[0]    = self.__ReadData(SensorLib.THRESHIGHLOW)
        HighThreshold[1]    = self.__ReadData(SensorLib.THRESHIGHHIGH)
        return HighThreshold

    #Interrupt control changing function here
    def GetPartNumber(self):
        return self.__ReadData(SensorLib.ID)[7:4]

    def GetRevNumber(self):
        return self.__ReadData(SensorLib.ID)[3:0]

    def ReadADC0(self): #Visible and IR
        Data    = bytearray(2)
        Data[0] = int(self.__ReadData(SensorLib.DATA0LOW))
        Data[1] = int(self.__ReadData(SensorLib.DATA0HIGH))
        return Data

    def ReadADC1(self): #Just IR
        Data        = bytearray(2)
        Data[0] = self.__ReadData(SensorLib.DATA1LOW)
        Data[1] = self.__ReadData(SensorLib.DATA1HIGH)
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
