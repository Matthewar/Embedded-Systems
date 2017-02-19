####################################################################################################
#NOTE: Some sections of this library have been commented out
## This is because it is too large to use with the other libraries and only limited
## functionality is needed
####################################################################################################
import ustruct

class TCS34725Lib:
    #Constants
    #- Slave Addr
    __SLAVE_ADDR = 0x29
    #- I2C Command Bits
    __COMMAND_CMD_BIT = 0x80
    __COMMAND_TYPE_BITS = {
        "RPT"   : 0x00, #Repeated byte protocol transaction
        "AUTO"  : 0x20, #Auto-increment protocol transaction
        "SPEC"  : 0x60 #Special function
    }
    __COMMAND_SF_BITS = 0x06
    #- I2C Enable Register Bits

    #Types
    #- Registers
    INTERNAL_REGISTER = {
        "ENABLE"    : 0x00, #Enables states and interrupts
        #"ATIME"     : 0x01, #RGBC time
        #"WTIME"     : 0x03, #Wait time
        #"AILTL"     : 0x04, #Clear interrupt low threshold low byte
        #"AILTH"     : 0x05, #Clear interrupt low threshold high byte
        #"AIHTL"     : 0x06, #Clear interrupt high threshold low byte
        #"AIHTH"     : 0x07, #Clear interrupt high threshold high byte
        #"PERS"      : 0x0C, #Interrupt persistence filter
        #"CONFIG"    : 0x0D, #Configuration
        #"CONTROL"   : 0x0F, #Control
        "ID"        : 0x12, #Device ID
        "STATUS"    : 0x13, #Device status
        "CDATAL"    : 0x14, #Clear data low byte
        #"CDATAH"    : 0x15, #Clear data high byte
        "RDATAL"    : 0x16, #Red data low byte
        #"RDATAH"    : 0x17, #Red data high byte
        "GDATAL"    : 0x18, #Green data low byte
        #"GDATAH"    : 0x19, #Green data high byte
        "BDATAL"    : 0x1A, #Blue data low byte
        #"BDATAH"    : 0x1B  #Blue data high byte
    }
    #- RGBC Timing
    RGBC_INTEG_CYCLES = {
    #Integ cycles : Value, Time, Max Count
        1   : 0xFF, #2.4ms, 1024
        10  : 0xF6, #24ms, 10240
        42  : 0xD5, #101ms, 43008
        64  : 0xC0, #154ms, 65535
        256 : 0x00  #700ms, 65535
    }
    #- Wait Times for WTIME reg
    WAIT_TIMES = {
    #Wait time : Reg value, Time (WLONG = 0), Time (WLONG = 1)
        1   : 0xFF, #2.4ms, 0.029s
        85  : 0xAB, #204ms, 2.45s
        256 : 0x00  #614ms, 7.4s
    }
    ##- Persistence Values
    #PERS_VALUES = {
    #    0   : 0x0, #Every RGBC cycle generates an interrupt
    #    1   : 0x1, #1 clear channel consecutive values out of range
    #    2   : 0x2, #2 clear channel consecutive values out of range
    #    3   : 0x3, #3 clear channel consecutive values out of range
    #    5   : 0x4, #5 clear channel consecutive values out of range
    #    10  : 0x5, #10 clear channel consecutive values out of range
    #    15  : 0x6, #15 clear channel consecutive values out of range
    #    20  : 0x7, #20 clear channel consecutive values out of range
    #    25  : 0x8, #25 clear channel consecutive values out of range
    #    30  : 0x9, #30 clear channel consecutive values out of range
    #    35  : 0xA, #35 clear channel consecutive values out of range
    #    40  : 0xB, #40 clear channel consecutive values out of range
    #    45  : 0xC, #45 clear channel consecutive values out of range
    #    50  : 0xD, #50 clear channel consecutive values out of range
    #    55  : 0xE, #55 clear channel consecutive values out of range
    #    60  : 0xF  #60 clear channel consecutive values out of range
    #}
    #- Control register bits (RGBC gain)
    RGBC_GAINS = {
        1   : 0x0, #1x gain
        4   : 0x1, #4x gain
        16  : 0x2, #16x gain
        60  : 0x3  #60x gain
    }

    #Constructor
    def __init__(self,i2c):
        self.i2c = i2c; #Keep reference of I2C module
        self.__regEnable = 0x00 #Enable register initial value

    #Writes data to a particular register (or two registers)
    def __WriteData(self,reg,data,length):
        if length == 1: #Single byte, pack as data
            sendData = ustruct.pack("<B",data)
        elif length == 2: #Multibyte, pack as data
            sendData = ustruct.pack("<H",data)
        else: #Otherwise, doesn't accept this
            raise Exception("Unsupported data write length")
        reg |= TCS34725Lib.__COMMAND_CMD_BIT | TCS34725Lib.__COMMAND_TYPE_BITS["AUTO"] #Add bit to access command register and setup auto write next byte
        self.i2c.writeto_mem(TCS34725Lib.__SLAVE_ADDR, reg, sendData) #Write to register

    #Read data from a particular register (or two registers)
    def __ReadData(self,reg,length):
        reg |= TCS34725Lib.__COMMAND_CMD_BIT | TCS34725Lib.__COMMAND_TYPE_BITS["AUTO"] #Add bits to access command register and setup auto read next byte
        data = self.i2c.readfrom_mem(TCS34725Lib.__SLAVE_ADDR, reg, length) #Read register (length number of bytes)
        if length == 1: #Single byte, unpack data as byte
            return ustruct.unpack("<B",data)[0]
        elif length == 2: #Multibyte, unpack data as short
            return ustruct.unpack("<H",data)[0]
        else: #Otherwise doesn't accept this
            raise Exception("Unsupported data read length")

    #Clear Current Interrupt
    def ClrIntr(self):
        #Address command reg, special mode: clear interrupt
        reg = 0x00 | TCS34725Lib.__COMMAND_CMD_BIT | TCS34725Lib.__COMMAND_TYPE_BITS["SPEC"] | TCS34725Lib.__COMMAND_SF_BITS
        self.i2c.writeto_mem(TCS34725Lib.__SLAVE_ADDR, reg, b'\x00') #Write command

    #Enable interrupt for RGBC detection
    def EnableIntrRGBC(self):
        self.__regEnable |= 0x10 #Set AIEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Disable interrupt for RGBC detection
    def DisableIntrRGBC(self):
        self.__regEnable &= 0xEF #Clear AIEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Enable wait timers
    def EnableWaitTimer(self):
        self.__regEnable |= 0x08 #Set WEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Disable wait timers
    def DisableWaitTimer(self):
        self.__regEnable &= 0xF7 #Clear WEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Enable RGBC detection
    def EnableRGBC(self):
        self.__regEnable |= 0x02 #Set AEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Disable RGBC detection
    def DisableRGBC(self):
        self.__regEnable &= 0xFD #Clear AEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Turn on device
    def PowerOn(self):
        self.__regEnable |= 0x01 #Set PON bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Turn off device
    def PowerOff(self):
        self.__regEnable &= 0xFE #Clear PON bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    #Set timing mode of device
    def SetRGBCTiming(self,mode):
        if mode in TCS34725Lib.RGBC_INTEG_CYCLES: #If mode exists, write to device
            self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ATIME"],TCS34725Lib.RGBC_INTEG_CYCLES[mode],1)
        else: #Otherwise error
            raise Exception("Unexpected timing mode")

    #Set size of wait timer
    def SetWaitTime(self,wait):
        if wait in TCS34725Lib.WAIT_TIMES: #If wait time exists, write to device
            self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["WTIME"],TCS34725Lib.WAIT_TIMES[wait],1)
        else: #Otherwise error
            raise Exception("Unexpected wait time")

    #Set lower interrupt threshold
    def SetRGBCLowIntr(self,value):
        if value > 255 or value < 0: #Make sure value is within unsigned byte size
            raise Exception("Value out of bounds")
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["AILTL"],value,2)

    #Set higher interrupt threshold
    def SetRGBCHighIntr(self,value):
        if value > 255 or value < 0: #Make sure value is within unsigned byte size
            raise Exception("Value out of bounds")
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["AIHTL"],value,2)

    ##Set persistence of interrupt
    #def SetIntrPers(self,pers):
    #    self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["PERS"],TCS34725Lib.PERS_VALUES[pers],1)

    #Set wait long mode
    def SetWaitLong(self): #Wait long: when asserted wait cycles are increased by a factor 12x from WTIME reg
        WLONG_BIT = 0x02 #Wait long command bits
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["CONFIG"],WLONG_BIT,1)

    #Turn off wait long mode
    def UnsetWaitLong(self):
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["CONFIG"],0x00,1)

    #Set gain of RGBC device
    def SetRGBCGain(self,gain):
        if gain in TCS34725Lib.RGBC_GAINS: #If actual gain value, write to device
            self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["CONTROL"],TCS34725Lib.RGBC_GAINS[gain],1)
        else: #Otherwise error
            raise Exception("Invalid gain value")

    #Get ID of device
    def GetID(self):
        idVal = self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["ID"],1) #Get ID
        #Convert to string
        if idVal == 0x44:
            return "TCS34721/TCS347235"
        elif idVal == 0x4D:
            return "TCS34723/TCS34727"
        else: #If non acceptable value, return error
            raise Exception("Error reading ID")

    #Get value of clear colour interrupt
    def GetRGBCIntrClr(self):
        return (self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["STATUS"],1) & 0x10) >> 4

    #Check if RGBC integration cycle is complete
    def GetRGBCValid(self):
        return self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["STATUS"],1) & 0x01

    #Get value of clear colour data
    def GetClearDataByte(self):
        return self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["CDATAL"],2)

    #Get value of red colour data
    def GetRedDataByte(self):
        return self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["RDATAL"],2)

    #Get value of green colour data
    def GetGreenDataByte(self):
        return self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["GDATAL"],2)

    #Get value of blue colour data
    def GetBlueDataByte(self):
        return self.__ReadData(TCS34725Lib.INTERNAL_REGISTER["BDATAL"],2)
