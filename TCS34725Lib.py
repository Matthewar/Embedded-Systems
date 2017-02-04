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
    __COMMAND_SF_BITs = 0x06
    #- I2C Enable Register Bits

    #Types
    #- Registers
    INTERNAL_REGISTER = {
        "ENABLE"    : 0x00, #Enables states and interrupts
        "ATIME"     : 0x01, #RGBC time
        "WTIME"     : 0x03, #Wait time
        "AILTL"     : 0x04, #Clear interrupt low threshold low byte
        "AILTH"     : 0x05, #Clear interrupt low threshold high byte
        "AIHTL"     : 0x06, #Clear interrupt high threshold low byte
        "AIHTH"     : 0x07, #Clear interrupt high threshold high byte
        "PERS"      : 0x0C, #Interrupt persistence filter
        "CONFIG"    : 0x0D, #Configuration
        "CONTROL"   : 0x0F, #Control
        "ID"        : 0x12, #Device ID
        "STATUS"    : 0x13, #Device status
        "CDATAL"    : 0x14, #Clear data low byte
        "CDATAH"    : 0x15, #Clear data high byte
        "RDATAL"    : 0x16, #Red data low byte
        "RDATAH"    : 0x17, #Red data high byte
        "GDATAL"    : 0x18, #Green data low byte
        "GDATAH"    : 0x19, #Green data high byte
        "BDATAL"    : 0x1A, #Blue data low byte
        "BDATAH"    : 0x1B  #Blue data high byte
    }

    def __init__(self,i2c):
        self.i2c = i2c;
        self.__regEnable = 0x00 #Enable register initial value

    def __WriteData(self,reg,data,length):
        if length == 1:
            sendData = ustruct.pack("<B",data)
        elif length == 2:
            sendData = ustruct.pack("<H",data)
        else:
            raise Exception("Unsupported data write length")
        reg |= __COMMAND_CMD_BIT | __COMMAND_TYPE_BITS["AUTO"]
        self.i2c.writeto_mem(TCS34725Lib.__SLAVE_ADDR, reg, sendData)

    def __ReadData(self,reg,length):
        reg |= __COMMAND_CMD_BIT | __COMMAND_TYPE_BITS["AUTO"]
        data = self.i2c.readfrom_mem(TCS34725Lib.__SLAVE_ADDR, reg, length)
        if length == 1:
            return ustruct.unpack("<B",data[0])[0]
        elif length == 2:
            return ustruct.unpack("<H",data)[0]
        else:
            raise Exception("Unsupported data read length")

    def ClrIntr(self):
        reg = 0x00 | TCS34725Lib.__COMMAND_CMD_BIT | TCS34725Lib.__COMMAND_TYPE_BITS["SPEC"] | TCS34725Lib.__COMMAND_SF_BITs
        self.i2c.writeto_mem(TCS34725Lib.__SLAVE_ADDR, reg, '\x00')

    def EnableIntrRGBC(self):
        self.__regEnable |= 0x10 #Set AIEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def DisableIntrRGBC(self):
        self.__regEnable &= 0xEF #Clear AIEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def EnableWaitTimer(self):
        self.__regEnable |= 0x08 #Set WEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def DisableWaitTimer(self):
        self.__regEnable &= 0xF7 #Clear WEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def EnableRGBC(self):
        self.__regEnable |= 0x02 #Set AEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def DisableRGBC(self):
        self.__regEnable &= 0xFD #Clear AEN bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def PowerOn(self):
        self.__regEnable |= 0x01 #Set PON bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

    def PowerOff(self):
        self.__regEnable &= 0xFE #Clear PON bit
        self.__WriteData(TCS34725Lib.INTERNAL_REGISTER["ENABLE"],self.__regEnable,1)

#ADDR    NAME    R/W Reset   Function
#-------------------------------------
#----    COMMAND W   0x00    Specifies reg address
#0x00    ENABLE  RW  0x00    Enables states and interrupts
#0x01    ATIME   RW  0xFF    RGBC time
#0x03    WTIME   RW  0xFF    Wait time
#0x04    AILTL   RW  0x00    Clear interrupt low threshold low byte
#0x05    AILTH   RW  0x00    Clear interrupt low threshold high byte
#0x06    AIHTL   RW  0x00    Clear interrupt high threshold low byte
#0x07    AIHTH   RW  0x00    Clear interrupt high threshold high byte
#0x0C    PERS    RW  0x00    Interrupt persistence filter
#0x0D    CONFIG  RW  0x00    Configuration
#0x0F    CONTROL RW  0x00    Control
#0x12    ID      R   ID      Device ID
#0x13    STATUS  R   0x00    Device status
#0x14    CDATAL  R   0x00    Clear data low byte
#0x15    CDATAH  R   0x00    Clear data high byte
#0x16    RDATAL  R   0x00    Red data low byte
#0x17    RDATAH  R   0x00    Red data high byte
#0x18    GDATAL  R   0x00    Green data low byte
#0x19    GDATAH  R   0x00    Green data high byte
#0x1A    BDATAL  R   0x00    Blue data low byte
#0x1B    BDATAH  R   0x00    Blue data high byte
