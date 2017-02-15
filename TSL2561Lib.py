import ustruct

#?? Change some values to constants for readability

class TSL2561Lib:
    #Constants
    #- Read Data (bits used for I2C)
    __COMMAND_BIT   = 0x80
    __WORD_BIT      = 0x20
    __INTR_CLR_BIT  = 0x40

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
    #- Timing Controller (Integration Time)
    INTEG_TIME = {
        #Nominal integration time : Integration Field Value
        "13.7ms"    : 0x0, #Scale 0.034
        "101ms"     : 0x1, #Scale 0.252
        "402ms"     : 0x2, #Scale 1
        "MAN"       : 0x3, #Scale N/A, NOTE: Only for manual mode (integration controlled by manual bit)
    }
    #- Interrupt Control Reg Constants
    #-- Control Select
    INTR_CTRL_SEL = {
        "OFF"   : 0x00, #Interrupt output disabled
        "LVL"   : 0x10, #Level interrupt
        "SMB"   : 0x20, #SMBAlert Compliant ?? May need function to respond
        "TST"   : 0x30, #Test mode: Sets interrupt and functions as mode 10 ?? May need SMB function to respond
    }
    #-- Persistence Select
    INTR_PERS_SEL = (
        0x0,    #Every ADC cycle generates interrupt
        0x1,    #Any value outside of threshold range
        0x2,    #2 integration time periods out of range
        0x3,    #3 integration time periods out of range
        0x4,    #4 integration time periods out of range
        0x5,    #5 integration time periods out of range
        0x6,    #6 integration time periods out of range
        0x7,    #7 integration time periods out of range
        0x8,    #8 integration time periods out of range
        0x9,    #9 integration time periods out of range
        0xA,    #10 integration time periods out of range
        0xB,    #11 integration time periods out of range
        0xC,    #12 integration time periods out of range
        0xD,    #13 integration time periods out of range
        0xE,    #14 integration time periods out of range
        0xF     #15 integration time periods out of range
    )
    #- Possible I2C addresses (depending on connection of ADDR pin)
    SLAVE_ADDRS = {
        "GND"   : 0x29, #0101001/49
        "FLOAT" : 0x39, #0111001/57
        "VDD"   : 0x49  #1001001/73
    }

    #Constructor
    def __init__(self,i2c,addr="FLOAT"):
        #Load I2C object passed
        self.i2c = i2c
        #Set Slave Address
        self.__SLAVE_ADDR = TSL2561Lib.SLAVE_ADDRS[addr]
        # Internal State
        self.__deviceOn = False
        self.__regTiming = 0x00 #Timing Register contents ?? Load from device instead of using default
        self.__regIntrCtrl = 0x00 #Interrupt Control Register contents ?? Load from device instead of using default

    def __WriteData(self,reg,data,twoBytes=False):
        reg |= TSL2561Lib.__COMMAND_BIT #Prepare address for device format
        #?? Need to add word bit if data is longer
        if twoBytes: #Multibyte, pack as data
            reg |= TSL2561Lib.__WORD_BIT #Add word bit since writing a word
            sendData = ustruct.pack("<H",data)
        else: #Single byte, pack as data
            sendData = ustruct.pack("<B",data)
        self.i2c.writeto_mem(self.__SLAVE_ADDR, reg, data) #?? Check ACKs received and resend if necessary ?? Need to convert Data to bytes

    def __ReadData(self,reg,twoBytes=False):
        reg |= TSL2561Lib.__COMMAND_BIT #Prepare address for device format
        if twoBytes:
            reg |= TSL2561Lib.__WORD_BIT #Add word bit since reading a word
            data = self.i2c.readfrom_mem(self.__SLAVE_ADDR, reg, 2) #Read two bytes
            return ustruct.unpack("<H",data)[0] #Convert from unsigned short to integer
        else:
            data = self.i2c.readfrom_mem(self.__SLAVE_ADDR, reg, 1)[0] #Read single byte
            return ustruct.unpack("<B",data)[0] #Convert from unsigned byte to int

    def PowerOn(self,force=False):
        if not self.__deviceOn or force:
            self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["CONTROL"],0x03)
            if (self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["CONTROL"]) != 0x03):
                raise Exception("I2C power up failed")
            else:
                self.__deviceOn = True

    def PowerOff(self,force=False):
        if self.__deviceOn or force:
            self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["CONTROL"],0x00)
            if (self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["CONTROL"]) != 0x00):
                raise Exception("I2C power down failed")
            else:
                self.__deviceOn = False

    def SetGainMode(self,mode):
        if mode: #X16 mode
            self.__regTiming |= 0x10 #Write a 1 to bit 4
        else: #X1 mode
            self.__regTiming &= 0xEF #Write a 0 to bit 4
        self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["TIMING"],self.__regTiming)

    def GetGainMode(self):
        return self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["TIMING"]) & 0x10 #Get bit 4 of TIMING reg

    def ChangeTiming(self,timingSetting):
        if not timingSetting in TSL2561Lib.INTEG_TIME:
            raise Exception("Timing setting is not valid")
        self.__regTiming &= 0xF0 #Clear lower 4 bits (related to timing)
        self.__regTiming |= TSL2561Lib.INTEG_TIME[timingSetting] #Set INTEG bits (integration time for conversion)
        self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["TIMING"],self.__regTiming)

    def StartIntegCycle(self):
        if self.__regTiming & 0x03 != 0x03:
            raise Exception("Attempting to start integration cycle while not in manual timing mode")
        self.__regTiming |= 0x08 #Set manual timing bit
        self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["TIMING"],self.__regTiming)

    def EndIntegCycle(self):
        if self.__regTiming & 0x0B == 0x03:
            raise Exception("Attempted to stop integration cycle while it was not running")
        elif self.__regTiming & 0x03 != 0x03:
            raise Exception("Attempting to stop interation cycle while not in manual timing mode")
        self.__regTiming &= 0xF7 #Clear manual timing bit
        self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["TIMING"],self.__regTiming)

    def SetIntrThreshold(self,low,high):
        if low is not None:
            if low > 255 or low < 0:
                raise Exception("Low value out of bounds")
            else:
                data = ustruct.pack("<H",low)
                self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["THRESLOWLOW"],data,True)
        if high is not None:
            if high > 255 or high < 0:
                raise Exception("High value out of bounds")
            else:
                data = ustruct.pack("<H",high)
                self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["THRESHIGHLOW"],data,True)

    def GetIntrLowThreshold(self):
        return self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["THRESLOWLOW"],True)

    def GetIntrHighThreshold(self):
        return self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["THRESHIGHLOW"],True)

    def SetIntrCtrlSel(self,read):
        self.__regIntrCtrl &= 0xCF #Clear INTR field value
        self.__regIntrCtrl |= TSL2561Lib.INTR_CTRL_SEL[read] #Combine new INTR field
        self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["INTERRUPT"],self.__regIntrCtrl,True)

    def SetIntrPersSel(self,func):
        self.__regIntrCtrl &= 0xF0 #Clear PERSIST field value
        self.__regIntrCtrl |= TSL2561Lib.INTR_PERS_SEL[func] #Combine new PERSIST field
        self.__WriteData(TSL2561Lib.INTERNAL_REGISTER["INTERRUPT"],self.__regIntrCtrl,True)

    def ClrIntr(self):
        self.i2c.writeto_mem(self.__SLAVE_ADDR, TSL2561Lib.__INTR_CLR_BIT, 0)

    def GetPartNumber(self):
        partNo = self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["ID"])
        if partNo: #If bits 7:4 = 0001, TSL2561, else TSL2560
            return "TSL2561"
        else:
            return "TSL2560"

    def GetRevNumber(self):
        return self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["ID"]) & 0x0F #Revision number is lower 4 bits of reg

    def ReadADC0(self): #Visible and IR
        return self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["DATA0LOW"],True)

    def ReadADC1(self): #Just IR
        return self.__ReadData(TSL2561Lib.INTERNAL_REGISTER["DATA1LOW"],True)

    def GetLux(self):
        ch0 = ReadADC0()
        ch1 = ReadADC1()
        ratio = ch1/ch0
        if ratio < 0:
            raise Exception("Somehow negative ratio occurred")
        elif ratio <= 0.52:
            lux = 0.0315 * ch0 - 0.0593 * ch0 * pow(ratio,1.4)
        elif ratio <= 0.65:
            lux = 0.0229 * ch0 - 0.0291 * ch1
        elif ratio <= 0.8:
            lux = 0.0157 * ch0 - 0.0180 * ch1
        elif ratio <= 1.3:
            lux = 0.00338 * ch0 - 0.00260 * ch1
        else:
            lux = 0
        return lux

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
