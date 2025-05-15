from lcd19264 import LCD19264
from time import sleep

lcd = LCD19264(rs = 1, rw = 2, en = 3, rst = 13, cs1 = 12, cs2 = 14, cs3 = 15,
                  db0 = 4, db1 = 5, db2 = 6, db3 = 7, db4 = 8, db5 = 9, db6 = 10, db7 = 11)
#lcd.set_rotation()

SCREEN_WIDTH  = lcd.width
SCREEN_HEIGHT = lcd.height

lcd.fill(0) # clear

lcd.ellipse(25, 25, 20, 20, 1, True)
lcd.ellipse(70, 40, 20, 20, 1)

lcd.pixel(25, 25, 0)
lcd.pixel(70, 40, 1)

lcd.rect(100, 5, 35, 35, 1, True)
lcd.rect(145, 25, 35, 35, 1)

for y in range(SCREEN_HEIGHT // 4):
    lcd.line(0, 0, SCREEN_WIDTH, y * 4 , 1)

lcd.show()
