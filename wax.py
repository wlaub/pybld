import time
import curses
import pdb
import image

"""
test = image.Frame()
#test.lines[0][(0,0)] = 'TEST'
#test.lines[1][(1,0)] = 'GREEN'
data = "\x01\x03\x03\x03\x03\x02AB\x02\x81\xc1\xc2\x81\x20\x20\x20\x20"
data = ['\x01']
data.extend(['\x03']*60*6)
data.extend(['\x02']*60*6)
data.extend(['\x01']*60*6)
data.extend(['\x00']*60*6)


data = ''.join(data)
test.load(data, 24,60)

timg = image.Image()
timg.frames.append(test)
timg.save("img/test.bmi")
"""
test = image.Image()
test.load("img/test.bmi")

try:
    window = curses.initscr()
    window = curses.newwin(24,60,0,0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)

 

    while 1:
        time.sleep(.1)
        test.draw(window,0,0)        
        window.refresh()

except:
    curses.endwin()
    raise
finally:
    curses.endwin()


