"""
v0.1.4

DB_LCD19264 is a FrameBuffer based MicroPython driver for the graphical
LiquidCrystal LCD19264 display
Сonnection used: Data bus 8-bit

Project path: https://github.com/r2d2-arduino/micropython-lcd19264

Author:
  16 june 2024 - r2d2-arduino

Pinout
==============================
1	Vss		GND
2	Vdd		+5V
3	Vo		Operating voltage for LCD
4	RS		H:Data L:Command
5	R/W		H:Read L:Write
6	E		Enable signal
7	DB0		}
...	DB..	} Data bus 8-bit
14	DB7		}
15	CS1		Chip 1 selection L: Active
17	CS2		Chip 2 selection L: Active
18	CS3		Chip 3 selection L: Active
19	Vout	-10v Out voltage for LCD driving
20	LED+	+5v LED backlight

3 and 19 pins are used to adjust the display contrast through a resistor.
I use a 1 Mega Ohm variable resistor. Acceptable contrast ~270kOm

"""
import framebuf
import time
from machine import Pin

LCD_WIDTH = 192
LCD_HEIGHT = 64

LCD_ADDR         = const(0x80)
LCD_DISPLAY_ON   = const(0x3F)
LCD_DISPLAY_OFF  = const(0x3E)
LCD_ADDR_Y       = const(0x40)
LCD_ADDR_X       = const(0xB8)
LCD_ADDR_Z       = const(0xC0)
LCD_EMPTY        = const(0x00)

class DB_LCD19264( framebuf.FrameBuffer ):
    def __init__( self, rs, rw, en, rst, cs1, cs2, cs3, db0, db1, db2, db3, db4, db5, db6, db7 ):

        self.rs = Pin( rs, Pin.OUT )
        self.rw = Pin( rw, Pin.OUT )
        self.en = Pin( en, Pin.OUT )
        self.rst = Pin( rst, Pin.OUT )
        
        self.cs1 = Pin( cs1, Pin.OUT )
        self.cs2 = Pin( cs2, Pin.OUT )
        self.cs3 = Pin( cs3, Pin.OUT )
        
        self.db = [0, 1, 2, 3, 4, 5, 6, 7]
        
        self.db[0] = Pin( db0, Pin.OUT )
        self.db[1] = Pin( db1, Pin.OUT )
        self.db[2] = Pin( db2, Pin.OUT )
        self.db[3] = Pin( db3, Pin.OUT )
        self.db[4] = Pin( db4, Pin.OUT )
        self.db[5] = Pin( db5, Pin.OUT )
        self.db[6] = Pin( db6, Pin.OUT )
        self.db[7] = Pin( db7, Pin.OUT )

        self.height = LCD_HEIGHT
        self.width  = LCD_WIDTH
        
        self._reverse = False
        
        #order of bites in buffer depending of screen position
        _bufFormat = framebuf.MONO_VLSB
            
        # Initialize the FrameBuffer
        self._bufsize = (self.width * self.height)//8
        self._buffer = bytearray( self._bufsize ) # 8 pixels per Bytes MONO_VLSB (1bit/pixel, 7th bit the topmost pixel)
        self._memoview = memoryview(self._buffer)
        super().__init__(
                        self._buffer,
                        self.width, # pixels width
                        self.height, # pixels height
                        _bufFormat # 1 bit per pixel, 7th bit the leftmost pixel
                )

        self._init()
        self.clear()
        
    # Display init
    def _init(self):
        self.rst.off()  # Reset
        time.sleep_ms(1)
        self.rst.on()
        self.cs1.off()  # Choose CS1
        self.cs2.off()  # Choose CS2
        self.cs3.off()  # Choose CS3
        
        self._write_cmd(LCD_DISPLAY_ON)  # Display On
        self._write_cmd(LCD_ADDR_Z)  # Set begin position (top left corner)
        
    # Send command to display
    @micropython.viper
    def _write_cmd(self, cmd: int):
        self.rs.off()  # RS = 0 (Command)
        self.rw.off()  # RW = 0 (Write)
        
        self._write_data_bus(cmd)
        
        self.en.on()
        time.sleep_us(1)
        self.en.off()
        time.sleep_us(1)
        
    # Write Data Bus
    @micropython.viper
    def _write_data_bus(self, data: int):
        self.db[0].value(data & 1)
        self.db[1].value(data & (1 << 1))
        self.db[2].value(data & (1 << 2))
        self.db[3].value(data & (1 << 3))
        self.db[4].value(data & (1 << 4))
        self.db[5].value(data & (1 << 5))
        self.db[6].value(data & (1 << 6))
        self.db[7].value(data & (1 << 7))

        
    # Read Data Bus
    def _read_data_bus(self):
        data = 0
        for i in range(8):
            data |= self.db[i].value() << i
            
        return data        


    # Read display status
    def status(self):
        self.rs.off()  # RS = 0 (Command)
        self.rw.on()   # RW = 1 (Read)
        self.en.on()
        
        status = self._read_data_bus()
        
        self.en.off()
        return status

    # Write data
    @micropython.viper
    def _write_data(self, data: int):
        self.rs.on()  # RS = 1 (Data)
        self.rw.off()  # RW = 0 (Write)
        self._write_data_bus(data)
        self.en.on()
        time.sleep_us(1)
        self.en.off()
        time.sleep_us(1)

    # Clear display
    def clear(self):
        self.fill( 0 ) # Clear FrameBuffer
        
        for chip in range(1, 4):
            self._select_chip(chip) #Set chip
            #self._write_cmd(LCD_DISPLAY_ON)  # Display On
            self._write_cmd(LCD_ADDR_Z)  # Set begin position (top left corner)
            for i in range(0, 64):
                for j in range(0, 8):
                    self._write_data(LCD_EMPTY)
                    
        self._select_chip(1)
        #self._write_cmd(LCD_DISPLAY_ON) # Display On

    # Choose part of display: 1-3
    @micropython.viper
    def _select_chip(self, chip: int):
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
            
    # Set address in column: 0-63
    @micropython.viper
    def _set_address(self, y: int):
        self._write_cmd(LCD_ADDR_Y + y)

        
    # Set address in row: 0-7
    @micropython.viper
    def _set_page(self, x: int):
        self._write_cmd(LCD_ADDR_X + x)
        
    # Shift start point:0-63
    @micropython.viper
    def _show_start(self, z: int):
        self._write_cmd(LCD_ADDR_Z + z)
    
    #Rotate display
    def set_rotation(self, reverse = True):
        self._reverse = reverse
            
    # Send FrameBuffer to lcd
    # reverse - revert 
    def show( self ):
        #start = time.ticks_ms()

        self._write_cmd(LCD_ADDR_Z)
        buf = self._memoview
        
        for chip in range(0, 3):
            self._select_chip(chip + 1)
            self._set_address(0) # Set begin position to 0
            for page in range(0, 8):
                self._set_page(page)
                #self._set_address(0) 
                
                self.rs.on()  # RS = 1 (Data)
                self.rw.off()  # RW = 0 (Write)
                
                posOffset = (page * 192) + (chip * 64)
                
                for address in range(0, 64):                    
                    if self._reverse:
                        self._write_data_bus(self._reverse_bits(buf[1535 - address - posOffset]))
                    else:
                        self._write_data_bus(buf[address + posOffset])
 
                    self.en.on()
                    time.sleep_us(1)
                    self.en.off()
                    time.sleep_us(1)                  
                    
        self._write_cmd(LCD_DISPLAY_ON)
        
        #print(time.ticks_diff(time.ticks_ms(), start)/1000)

    #Reverse bits 0100 0111 => 1110 0010
    @micropython.viper
    def _reverse_bits(self, x: int) -> int:#0.378
        result = 0
        if x & 1: result |= 1 << 7
        if (x >> 1) & 1: result |= 1 << 6
        if (x >> 2) & 1: result |= 1 << 5
        if (x >> 3) & 1: result |= 1 << 4
        if (x >> 4) & 1: result |= 1 << 3
        if (x >> 5) & 1: result |= 1 << 2
        if (x >> 6) & 1: result |= 1 << 1
        if (x >> 7) & 1: result |= 1
        return result
