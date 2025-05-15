from lcd19264_rp2 import LCD19264
from time import sleep
from bitmaps import sun, suncloud, rain, rainlight, snowman

lcd = LCD19264(rs = 1, rw = 2, en = 3, rst = 13, cs1 = 12, cs2 = 14, cs3 = 15,
                  db0 = 4, db1 = 5, db2 = 6, db3 = 7, db4 = 8, db5 = 9, db6 = 10, db7 = 11)
#lcd.set_rotation()

bitmaps = [sun, suncloud, rain, rainlight, snowman]
size = 16

for i in range( len( bitmaps ) ):
    lcd.fill(0) # clear
    bitmap = bitmaps[ i ]
    for x in range( 12 ):
        for y in range( 4 ):
            lcd.draw_bitmap( bitmap, x * size, y * size, 1 )
    lcd.show( )
    sleep( 1 )
    