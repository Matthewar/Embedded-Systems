from machine import I2C, Pin
from enum import Enum

#?? Move constants to shared file
SCL_PIN = 5
SDA_PIN = 4
##

class SensorLib:
    # Constants
    MIN_CLK_FREQ = 0
    MAX_CLK_FREQ = 400000
    # Internal State
    self.__DeviceOn = True
    # Types
    #- Register
    class InternalRegister(Enum):
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

    def __init__(self):
        #Initialise I2C class
        self.i2c = I2C(-1, Pin(SCL_PIN), Pin(SDA_PIN), SensorLib.MAX_CLK_FREQ)
        #?? Set address of slave device
        #Start I2C
        self.i2c.Start()

    def __del__(self):
        self.i2c.Stop()

    def __WriteData(self,Reg,Data):
        self.i2c.writeto_mem(SensorLib.SLAVE_ADDR, Reg, Data) #?? Declare SLAVE_ADDR ?? Check ACKs received and resend if necessary ?? Need to convert Data to bytes

    def __ReadData(self,Reg):
        return self.i2c.readfrom_mem(SensorLib.SLAVE_ADDR, Reg, 1)

    def PowerUp(Force=False): #?? Return values for these, include check for success?
        if not self.__DeviceOn or Force:
            __WriteData(CONTROL,3)
            self.__DeviceOn = True

    def PowerDown(Force=False): #?? Return values for these, include check for success?
        if self.__DeviceOn or Force:
            __WriteData(CONTROL,0)
            self.__DeviceOn = False


#Slave Addresses
##ADDR SEL TERMINAL LEVEL   ADDR
##GND                       0101001
##Float                     0111001
##VDD                       1001001

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
