from lcd19264 import LCD19264
import LibreBodoni24 as MY_FONT

# Set pins here
lcd = LCD19264(rs = 1, rw = 2, en = 3, rst = 13, cs1 = 12, cs2 = 14, cs3 = 15,
                  db0 = 4, db1 = 5, db2 = 6, db3 = 7, db4 = 8, db5 = 9, db6 = 10, db7 = 11)

#lcd.set_rotation()

lcd.fill( 0 )
lcd.set_font( MY_FONT )
lcd.set_text_wrap( )
lcd.text( "Default 8x8 font", 0, 0 )
lcd.draw_text( "Custom font:  LibreBodoni size 24", 0, 10 )

lcd.show()