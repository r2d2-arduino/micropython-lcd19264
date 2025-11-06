"""
v 0.2.1

LCD19264_RP2 is a FrameBuffer based MicroPython driver for the graphical
LiquidCrystal LCD19264 display.

Сonnection: Data bus 8-bit
Color: 1-bit monochrome
Controllers: Raspberry Pi Pico

Project path: https://github.com/r2d2-arduino/micropython-lcd19264
MIT Licenze

Author: Derkach Arthur

Pinout
==============================
1    Vss     GND
2    Vdd     +5V
3    Vo      Operating voltage for LCD
4    RS      H:Data L:Command
5    R/W     H:Read L:Write
6    E       Enable signal
7    DB0     }
..   DB..    } Data bus 8-bit
14   DB7     }
15   CS1     Chip 1 selection L: Active
16   RST     Reset L: Active
17   CS2     Chip 2 selection L: Active
18   CS3     Chip 3 selection L: Active
19   Vout    -10v Out voltage for LCD driving
20   LED+    +5v LED backlight

3 and 19 pins are used to adjust the display contrast through a resistor.
I use a 1 Mega Ohm variable resistor. Acceptable contrast ~270kOm

"""
from machine import Pin
from time import sleep_us
from draw_fb_mono import DRAW_FB_MONO

LCD_WIDTH        = const(192)
LCD_HEIGHT       = const(64)

LCD_ADDR         = const(0x80)
LCD_DISPLAY_ON   = const(0x3F)
LCD_DISPLAY_OFF  = const(0x3E)
LCD_ADDR_Y       = const(0x40)
LCD_ADDR_X       = const(0xB8)
LCD_ADDR_Z       = const(0xC0)
        
class LCD19264( DRAW_FB_MONO ):
    
    GPIO_OUT_REG = const(0xD0000010) # Registers for Raspberry Pi Pico
    
    def __init__( self, rs, rw, en, rst, cs1, cs2, cs3, db0, db1, db2, db3, db4, db5, db6, db7 ):
        ''' Main constructor '''
        
        #Initialization of pins
        self.rs  = Pin( rs, Pin.OUT, value = 1 )
        self.rw  = Pin( rw, Pin.OUT, value = 0 )
        self.en  = Pin( en, Pin.OUT, value = 0 )
        self.rst = Pin( rst, Pin.OUT, value = 1 )
        
        self.cs1 = Pin( cs1, Pin.OUT, value = 1 )
        self.cs2 = Pin( cs2, Pin.OUT, value = 1 )
        self.cs3 = Pin( cs3, Pin.OUT, value = 1 )
        
        self.db0 = Pin( db0, Pin.OUT, value = 0 )
        self.db1 = Pin( db1, Pin.OUT, value = 0 )
        self.db2 = Pin( db2, Pin.OUT, value = 0 )
        self.db3 = Pin( db3, Pin.OUT, value = 0 )
        self.db4 = Pin( db4, Pin.OUT, value = 0 )
        self.db5 = Pin( db5, Pin.OUT, value = 0 )
        self.db6 = Pin( db6, Pin.OUT, value = 0 )
        self.db7 = Pin( db7, Pin.OUT, value = 0 )

        self.height = LCD_HEIGHT
        self.width  = LCD_WIDTH
        
        self._rotation = 0     
            
        # Initialize the FrameBuffer
        super().__init__( self.width, self.height )
        
        self.en_bit  = 1 << en
        self.data_pins = [ db0, db1, db2, db3, db4, db5, db6, db7 ]
        self.data_mask = sum( 1 << pin for pin in self.data_pins ) + (1 << en)
        self.BYTE2GPIO = self.generate_byte2gpio()
        self.BYTE2RGPIO = self.generate_byte2rgpio() # revert version
        
        self._init()
        
    def _init( self ):
        ''' Display init '''
        self.rst.off()  # Reset
        sleep_us(1000)
        self.rst.on()
        self._select_chip(0)
        
        self.fill(0) # Clear FrameBuffer
        self._set_start(0)  # Set begin position (top left corner)
        self._write_cmd(LCD_DISPLAY_ON)  # Display On
        
        
    @micropython.viper
    def _write_cmd( self, cmd: int ):
        ''' Send command to display
        Args
        cmd (int): command number
        '''
        self.rs.off()  # RS = 0 (Command)
        self.rw.off()  # RW = 0 (Write)
        
        self._write_data_bus(cmd)
        
        self.en.on()
        sleep_us(1)
        self.en.off()
        sleep_us(1)
        
    @micropython.viper
    def _write_data( self, data: int ):
        ''' Single data write
        Args
        data (int): Byte of data
        '''
        self.rs.on()  # RS = 1 (Data)
        self.rw.off()  # RW = 0 (Write)
        self._write_data_bus(data)
        self.en.on()
        sleep_us(1)
        self.en.off()
        sleep_us(1)
        
    @micropython.viper
    def _write_data_bus( self, data: int ):
        ''' Write Data Bus
        Args
        data (int): Byte of data
        '''
        self.db0.value(data & 1)
        self.db1.value(data & (1 << 1))
        self.db2.value(data & (1 << 2))
        self.db3.value(data & (1 << 3))
        self.db4.value(data & (1 << 4))
        self.db5.value(data & (1 << 5))
        self.db6.value(data & (1 << 6))
        self.db7.value(data & (1 << 7))

    def _read_data_bus( self ):
        ''' Read Data Bus '''
        data = self.db0.value()
        data |= self.db1.value() << 1
        data |= self.db2.value() << 2
        data |= self.db3.value() << 3
        data |= self.db4.value() << 4
        data |= self.db5.value() << 5
        data |= self.db6.value() << 6
        data |= self.db7.value() << 7            
        return data        

    def generate_byte2gpio( self ):
        """ Generate to memory all 256 states of data gpio
        Return (bytearray): All 256 x 32-bit states """
        
        # Current GPIO values ​​excluding mask related bits
        byte2gpio32 = bytearray()

        for byte in range(256):
            gpio = self.convert_byte2gpio( byte ) 
            byte2gpio32 += gpio.to_bytes( 4, 'little' )
                
        return byte2gpio32
    
    def generate_byte2rgpio( self ):
        """ Generate to memory all 256 states of data gpio
        Return (bytearray): All 256 x 32-bit states """
        
        # Current GPIO values ​​excluding mask related bits
        byte2gpio32 = bytearray()
    
        for byte in range(256):
            rbyte = self._reverse_bits(byte)
            gpio = self.convert_byte2gpio(rbyte) 
            byte2gpio32 += gpio.to_bytes( 4, 'little' )
                
        return byte2gpio32    
                
    @micropython.viper
    def convert_byte2gpio( self, byte: int ) -> int:
        """
        Convert byte to gpio setting
        Params
        byte (int): Byte, example 0x27
        Return (int): gpio state, example 234889216 = '0b1110000000000010000000000000'
        """
        dpins = self.data_pins
        bit_pins = (byte & 1) << int(dpins[0])
        bit_pins |= ((byte >> 1) & 1) << int(dpins[1])
        bit_pins |= ((byte >> 2) & 1) << int(dpins[2])
        bit_pins |= ((byte >> 3) & 1) << int(dpins[3])
        bit_pins |= ((byte >> 4) & 1) << int(dpins[4])
        bit_pins |= ((byte >> 5) & 1) << int(dpins[5])
        bit_pins |= ((byte >> 6) & 1) << int(dpins[6])
        bit_pins |= ((byte >> 7) & 1) << int(dpins[7])
        return bit_pins 

    def status( self ):
        ''' Read display status
        Return (int): status
        '''
        self.rs.off()  # RS = 0 (Command)
        self.rw.on()   # RW = 1 (Read)
        self.en.on()
        
        status = self._read_data_bus()
        
        self.en.off()
        return status    

    @micropython.viper
    def _select_chip( self, chip: int ):
        ''' Choose part of display
        Args
        chip (int): 0..3 - Chip selection
        '''
        if chip == 1:
            self.cs1.off()
            self.cs2.on()
            self.cs3.on()
        elif chip == 2:
            self.cs1.on()
            self.cs2.off()
            self.cs3.on()
        elif chip == 3:
            self.cs1.on()
            self.cs2.on()
            self.cs3.off()        
        else:
            self.cs1.off()
            self.cs2.off()
            self.cs3.off()
            
    @micropython.viper
    def _set_address( self, y: int ):
        ''' Set column address
        Args
        y (int): 0..63 - Column address
        '''
        self._write_cmd(LCD_ADDR_Y + y)

    @micropython.viper
    def _set_page( self, x: int ):
        ''' Set row address 
        Args
        x (int): 0..7 - Row address
        '''        
        self._write_cmd(LCD_ADDR_X + x)
        
    @micropython.viper
    def _set_start( self, z: int ):
        ''' Shift start point
        Args
        z (int): 0..63 - Start point
        '''        
        self._write_cmd(LCD_ADDR_Z + z)
    
    def set_rotation( self, rotation = True ):
        ''' Set display orientation
        Args
        rotation (bool): True - rotation is On, False - reverse is Off
        '''
        self._rotation = int(rotation)
            
    @staticmethod
    @micropython.viper
    def _reverse_bits( byte: int ) -> int:
        ''' Reverse bits 0100 0111 => 1110 0010
        Args
        byte (int): Income byte
        Return (int): Reversed byte
        '''
        result = 0
        if byte & 1: result |= 1 << 7
        if (byte >> 1) & 1: result |= 1 << 6
        if (byte >> 2) & 1: result |= 1 << 5
        if (byte >> 3) & 1: result |= 1 << 4
        if (byte >> 4) & 1: result |= 1 << 3
        if (byte >> 5) & 1: result |= 1 << 2
        if (byte >> 6) & 1: result |= 1 << 1
        if (byte >> 7) & 1: result |= 1
        return result               
            
    @micropython.viper
    def clear( self ):
        ''' Clear display '''
        self.fill(0) # Clear FrameBuffer
        self.show() # Update screen     
            
    @micropython.viper
    def show( self ):
        ''' Send FrameBuffer to LCD '''
        buf = ptr8(self.buffer)
        addrSize = LCD_WIDTH * 8

        data_mask = int(self.data_mask)
        en_bit    = int(self.en_bit)
        rotation  = int(self._rotation)
        
        GPIO_OUT  = ptr32(GPIO_OUT_REG)
        
        if rotation:
            byte2gpio = ptr32(self.BYTE2RGPIO)
        else:
            byte2gpio = ptr32(self.BYTE2GPIO)
        
        self._set_start(0) # Set start point 0
        self._set_address(0) # Set begin position to 0
        
        for chip in range(0, 3):
            self._select_chip(chip + 1)
                            
            for page in range(0, 8):
                self._set_page(page)
                
                self.rs.on()  # RS = 1 (Data)
                self.rw.off()  # RW = 0 (Write)
                
                if page == 0:
                    empty_mask = GPIO_OUT[0] & ~data_mask

                posOffset = ( page * LCD_WIDTH) + (chip * LCD_HEIGHT )
                
                for address in range(0, LCD_HEIGHT):
                    pos = address + posOffset
                    
                    if rotation:
                        pos = addrSize - 1 - pos
                        
                    gpio = byte2gpio[ buf[ pos ] ] | empty_mask                 

                    GPIO_OUT[0] = gpio | en_bit
                    sleep_us(1)
                    GPIO_OUT[0] = gpio
                    sleep_us(1)
                
        self._write_cmd(LCD_DISPLAY_ON)
