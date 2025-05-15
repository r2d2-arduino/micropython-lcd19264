"""
v 0.1.10

LCD19264 is a FrameBuffer based MicroPython driver for the graphical
LiquidCrystal LCD19264 display.

Сonnection: Data bus 8-bit
Color: 1-bit monochrome
Controllers: Esp32-family, RP2

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
from framebuf import FrameBuffer, MONO_VLSB, MONO_HLSB
from time import sleep_us
from machine import Pin

LCD_WIDTH        = const(192)
LCD_HEIGHT       = const(64)
LCD_BUFFSIZE     = const( LCD_WIDTH * LCD_HEIGHT // 8 )

LCD_ADDR         = const(0x80)
LCD_DISPLAY_ON   = const(0x3F)
LCD_DISPLAY_OFF  = const(0x3E)
LCD_ADDR_Y       = const(0x40)
LCD_ADDR_X       = const(0xB8)
LCD_ADDR_Z       = const(0xC0)
LCD_EMPTY        = const(0x00)

class LCD19264( FrameBuffer ):
    def __init__( self, rs, rw, en, rst, cs1, cs2, cs3, db0, db1, db2, db3, db4, db5, db6, db7 ):
        ''' Main constructor '''
        
        #Initialization of pins
        self.rs  = Pin( rs, Pin.OUT )
        self.rw  = Pin( rw, Pin.OUT )
        self.en  = Pin( en, Pin.OUT )
        self.rst = Pin( rst, Pin.OUT )
        
        self.cs1 = Pin( cs1, Pin.OUT )
        self.cs2 = Pin( cs2, Pin.OUT )
        self.cs3 = Pin( cs3, Pin.OUT )
        
        self.db0 = Pin( db0, Pin.OUT )
        self.db1 = Pin( db1, Pin.OUT )
        self.db2 = Pin( db2, Pin.OUT )
        self.db3 = Pin( db3, Pin.OUT )
        self.db4 = Pin( db4, Pin.OUT )
        self.db5 = Pin( db5, Pin.OUT )
        self.db6 = Pin( db6, Pin.OUT )
        self.db7 = Pin( db7, Pin.OUT )

        self.height = LCD_HEIGHT
        self.width  = LCD_WIDTH
        
        self._rotation = 0
        self._text_wrap = False
        self._font = None

        # Alternative inverted palette for text
        self._palette = FrameBuffer( bytearray(2), 2, 1, MONO_HLSB )
        self._palette.pixel(0, 0, 1) # bg = 1
        self._palette.pixel(1, 0, 0) # fg = 0  
            
        # Initialize the FrameBuffer
        self.buffer = bytearray( LCD_BUFFSIZE ) 
        super().__init__( self.buffer, self.width, self.height, MONO_VLSB )

        self._init()
        
    def _init( self ):
        ''' Display init '''
        self.rst.off()  # Reset
        sleep_us(1000)
        self.rst.on()
        
        self.fill(0) # Clear FrameBuffer
        
        self._select_chip(0)        
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
        self.db0.value( data & 1 )
        self.db1.value( data & (1 << 1) )
        self.db2.value( data & (1 << 2) )
        self.db3.value( data & (1 << 3) )
        self.db4.value( data & (1 << 4) )
        self.db5.value( data & (1 << 5) )
        self.db6.value( data & (1 << 6) )
        self.db7.value( data & (1 << 7) )

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
        rotation (int): True - rotation is On, False - rotation is Off
        '''
        self._rotation = bool(rotation)
            
    @micropython.viper
    def _reverse_bits( self, byte: int ) -> int:
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
    def show( self ):
        ''' Send FrameBuffer to LCD '''
        # convert self to local variable
        db0, db1, db2, db3, db4, db5, db6, db7 = self.db0, self.db1, self.db2, self.db3, self.db4, self.db5, self.db6, self.db7
        en = self.en
        rotation = int(self._rotation)
        buffer  = ptr8(self.buffer)
        
        self._set_start(0)
        
        for chip in range(0, 3):
            self._select_chip(chip + 1)
            self._set_address(0) # Set begin position to 0
            for page in range(0, 8):
                self._set_page(page)
                #Data write mode
                self.rs.on()  # RS = 1 (Data)
                self.rw.off()  # RW = 0 (Write)
                
                posOffset = (page * LCD_WIDTH) + (chip * LCD_HEIGHT)
                
                for address in range(0, LCD_HEIGHT): 
                    if rotation:
                        data = int(self._reverse_bits(buffer[LCD_WIDTH * 8 - 1 - address - posOffset]))
                    else:
                        data = buffer[address + posOffset]
                        
                    db0.value(data & 1)
                    db1.value(data & (1 << 1))
                    db2.value(data & (1 << 2))
                    db3.value(data & (1 << 3))
                    db4.value(data & (1 << 4))
                    db5.value(data & (1 << 5))
                    db6.value(data & (1 << 6))
                    db7.value(data & (1 << 7))
 
                    en.on()
                    sleep_us(1)
                    en.off()                 
                    
        self._write_cmd(LCD_DISPLAY_ON)
 
    """ ADDITIONAL FUNCTIONS """
 
    def set_font( self, font ):
        """ Set font for text
        Args
        font (module): Font module generated by font_to_py.py
        """
        self._font = font

    def set_text_wrap( self, on = True ):
        """ Set text wrapping """
        self._text_wrap = bool( on )  

    def draw_text( self, text, x, y, color = 1 ):
        """ Draw text on framebuffer
        Args
        x (int) : Start X position
        y (int) : Start Y position
        """
        x_start = x
        screen_height = self.height
        screen_width  = self.width
        wrap = self._text_wrap
        
        font = self._font

        if font == None:
            print("Font not set")
            return False
        
        palette = self._palette

        for char in text:   
            glyph = font.get_ch(char)
            glyph_height = glyph[1]
            glyph_width  = glyph[2]
                
            if wrap and (x + glyph_width > screen_width): # End of row
                x = x_start
                y += glyph_height                
            
            fb = FrameBuffer( bytearray(glyph[0]), glyph_width, glyph_height, MONO_HLSB)
            if color:
                self.blit(fb, x, y)
            else:
                self.blit(fb, x, y, -1, palette)
            
            x += glyph_width

    @micropython.viper
    def draw_bitmap( self, bitmap, x:int, y:int, color:int ):
        """ Draw a bitmap on framebuffer
        Args
        bitmap (bytes): Bitmap data
        x      (int): Start X position
        y      (int): Start Y position
        color  (int): Color 0 or 1
        """
        fb = FrameBuffer( bitmap[0], bitmap[2], bitmap[1], MONO_HLSB )
        if color:
            self.blit(fb, x, y)
        else:            
            self.blit(fb, x, y, -1, self._palette)

    @micropython.viper
    def draw_bitmap_tran( self, bitmap, x:int, y:int, color:int ):
        """ Draw a transparent bitmap on display
        Args
        bitmap (bytes): Bitmap data
        x      (int): Start X position
        y      (int): Start Y position
        color  (int): Color 0 or 1
        """
        data   = ptr8(bitmap[0]) #memoryview to bitmap
        height = int(bitmap[1])
        width  = int(bitmap[2])
        
        i = 0
        for h in range(height):
            bit_len = 0
            while bit_len < width:
                byte = data[i]
                xpos = bit_len + x
                ypos = h + y                
                #Drawing pixels when bit = 1
                if (byte >> 7) & 1:
                    self.pixel(xpos    , ypos, color)
                if (byte >> 6) & 1:
                    self.pixel(xpos + 1, ypos, color)
                if (byte >> 5) & 1:
                    self.pixel(xpos + 2, ypos, color)
                if (byte >> 4) & 1:
                    self.pixel(xpos + 3, ypos, color)
                if (byte >> 3) & 1:
                    self.pixel(xpos + 4, ypos, color)
                if (byte >> 2) & 1:
                    self.pixel(xpos + 5, ypos, color)
                if (byte >> 1) & 1:
                    self.pixel(xpos + 6, ypos, color)
                if byte & 1:
                    self.pixel(xpos + 7, ypos, color)

                bit_len += 8
                i += 1

    def load_bmp( self, filename, x = 0, y = 0, color = 1 ):
        """ Load monochromatic BMP image on framebuffer
        Args
        filename (string): filename of image, example: "rain.bmp"
        x (int) : Start X position
        y (int) : Start Y position
        color  (int): Color 0 or 1
        """
        f = open(filename, 'rb')

        if f.read(2) == b'BM':  #header
            dummy    = f.read(8)
            offset   = int.from_bytes(f.read(4), 'little')
            dummy    = f.read(4) #hdrsize
            width    = int.from_bytes(f.read(4), 'little')
            height   = int.from_bytes(f.read(4), 'little')
            planes   = int.from_bytes(f.read(2), 'little')
            depth    = int.from_bytes(f.read(2), 'little')
            compress = int.from_bytes(f.read(4), 'little')

            if planes == 1 and depth == 1 and compress == 0: #compress method == uncompressed
                f.seek(offset)
                
                self._send_bmp_to_buffer( f, x, y, width, height, color)
            else:
                print("Unsupported planes, depth, compress:", planes, depth, compress )
                
        f.close()    
        
    @micropython.viper
    def _send_bmp_to_buffer( self, f, x:int, y:int, width:int, height:int, color:int ):
        """ Send bmp-file to buffer
        Args
        f (object File) : Image file
        x (int) : Start X position
        y (int) : Start Y position        
        width (int): Width of image frame
        height (int): Height of image frame
        color  (int): Color 0 or 1
        """        
        block_size = ((width + 31) // 32) * 4  
        total_size = height * block_size
        bitmap_size = height * width // 8
        
        bitmap = bytearray(bitmap_size)
        bitmap_buffer = ptr8(bitmap)
        
        image_data = f.read(total_size)
        image_buffer = ptr8(image_data)
        
        row_bytes = width // 8
        for row in range(height): 
            byte_offset = row_bytes * row 
            block_offset = block_size * row 
            for byte in range(row_bytes): 
                if color == 1:
                    bitmap_buffer[bitmap_size - 1 - byte_offset - byte] = image_buffer[block_offset + row_bytes - 1 - byte] ^ 0xff
                else:
                    bitmap_buffer[bitmap_size - 1 - byte_offset - byte] = image_buffer[block_offset + row_bytes - 1 - byte]

        fb = FrameBuffer(bitmap, width, height, MONO_HLSB)
        self.blit(fb, 0, 0)