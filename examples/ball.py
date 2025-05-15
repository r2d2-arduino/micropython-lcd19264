from lcd19264 import LCD19264
from time import sleep_ms

lcd = LCD19264(rs = 1, rw = 2, en = 3, rst = 13, cs1 = 12, cs2 = 14, cs3 = 15,
                  db0 = 4, db1 = 5, db2 = 6, db3 = 7, db4 = 8, db5 = 9, db6 = 10, db7 = 11)

lcd.fill(0)

radius = 4

x_border = lcd.width - 1
y_border = lcd.height - 1

prev_x = radius
prev_y = radius

x = radius
y = radius

x_speed = 2
y_speed = 2

while True:    
    lcd.ellipse(prev_x, prev_y, radius, radius, 0, True) # clear previos
    lcd.ellipse(x, y, radius, radius, 1, True)
    prev_x = x
    prev_y = y
    
    x += x_speed
    y += y_speed
    
    if x + radius > x_border or x - radius < 0:
        x_speed = -x_speed
        
    if y + radius > y_border or y - radius < 0:
        y_speed = -y_speed    
    
    lcd.show() 


    

