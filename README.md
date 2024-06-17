# micropython-lcd19264
Library for LCD 19264 display. Uses Framebuffer class. Sends data to display via Data bus.

![Image](./LCD19264.jpg)

**Pinout**
|N  | Name | Comments |
|---|------|------------------------------------|
|1  |	Vss |	GND
|2  |	Vdd	|	+5V
|3  |	Vo	|	Operating voltage for LCD
|4  |	RS	|	H:Data L:Command
|5  |	R/W	|	H:Read L:Write
|6  |	E		| Enable signal
|7  |	DB0	|	}
|...|	DB..|	} Data bus
|14 |	DB7	|	}
|15 |	CS1	|	Chip 1 selection L: Active
|17 |	CS2	|	Chip 2 selection L: Active
|18 |	CS3	|	Chip 3 selection L: Active
|19 |	Vout|	-10v Out voltage for LCD driving
|20 |	LED+|	+5v LED backlight

3 and 19 pins are used to adjust the display contrast through a resistor.
I use a 1 Mega Ohm variable resistor. Acceptable contrast ~270kOm

**Code example:**

```python
# Work on Raspbery Pi Pico. For other controllers - check available pins!

from DB_LCD19264 import DB_LCD19264

lcd = DB_LCD19264(rs= 29, rw = 28, en = 27, rst = 8, cs1 = 14, cs2 = 15, cs3 = 26,
                  db0 = 0, db1 = 1, db2 = 2, db3 = 3, db4 = 4, db5 = 5, db6 = 6, db7 = 7)

lcd.text('MicroPython!  1234567890', 0, 1, 1)
lcd.show()
