# This example works on Raspberry Pico. Other controllers may need different pins

from DB_LCD19264 import DB_LCD19264
import time

lcd = DB_LCD19264(rs= 29, rw = 28, en = 27, rst = 8, cs1 = 14, cs2 = 15, cs3 = 26,
                  db0 = 0, db1 = 1, db2 = 2, db3 = 3, db4 = 4, db5 = 5, db6 = 6, db7 = 7)
lcd.clear()
lcd.fill(0)

lcd.text('MicroPython!  1234567890', 0, 1, 1)
lcd.text('========================', 0, 10, 1)
lcd.text('192 x 64', 0, 20, 1)
lcd.text('17.06.2024 23:00', 0, 30, 1)
lcd.text('----------------', 0, 40, 1)
lcd.text('!"#;%:?*()_+,<>', 0, 50, 1)

lcd.vline(160, 30, 30, 1)
lcd.hline(0, 43, 192, 1)

lcd.show()


