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

    def __init__(self,i2c):
        self.i2c = i2c;

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
