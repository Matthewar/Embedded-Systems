from machine import I2C, Pin

#?? Move constants to shared file
SCL_PIN = 5
SDA_PIN = 4
##

class SensorLib:
    #Constants
    MIN_CLK_FREQ = 0
    MAX_CLK_FREQ = 400000
    #
    def __init__(self):
        #Initialise I2C class
        self.i2c = I2C(-1, Pin(SCL_PIN), Pin(SDA_PIN), MAX_CLK_FREQ)


#Slave Addresses
##ADDR SEL TERMINAL LEVEL   ADDR
##GND                       0101001
##Float                     0111001
##VDD                       1001001

#Registers
##ADDR    REG NAME        REG FUNC
##--      COMMAND         Specifies register address
##0h      CONTROL         Control of basic functions
##1h      TIMING          Integration time/gain control
##2h      THRESLOWLOW     Low byte of low interrupt threshold
##3h      THRESLOWHIGH    High byte of low interrupt threshold
##4h      THRESHIGHLOW    Low byte of high interrupt threshold
##5h      THRESHIGHHIGH   High byte of high interrupt threshold
##6h      INTERRUPT       Interrupt control
##7h      --              Reserved
##8h      CRC             Factory test (not a user register)
##9h      --              Reserved
##Ah      ID              Part number/Rev ID
##Bh      --              Reserved
##Ch      DATA0LOW        Low byte of ADC channel 0
##Dh      DATA0HIGH       High byte of ADC channel 0
##Eh      DATA1LOW        Low byte of ADC channel 1
##Fh      DATA1HIGH       High byte of ADC channel 1
