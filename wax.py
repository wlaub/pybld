import time, sys, os
import curses
from curses.textpad import Textbox
import pdb
import image, waxutil

"""
test = image.Frame()
data = "\x01\x03\x03\x03\x03\x02AB\x02\x81\xc1\xc2\x81\x20\x20\x20\x20"
data = ['\x01']
data.extend(['\x03']*60*3)
data.extend(['\x02']*60*3)
data.extend(['\x01']*60*3)
data.extend(['\x00']*60*3)


data = ''.join(data)
test.load(data, 13,60)


filename = "img/test.bmi"
timg = image.Image()
timg.frames.append(test)
timg.save(filename)
"""


filename = "img/test.bmi"

if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    filename = sys.argv[1]

test = image.Image()
test.load(filename)

editmode = False
drawalpha =False

def validator(data):
    if data == 0x1b:
        return 7
    if data >= 0x010a and data <= 0x0114:
        #Fix
        return data-0x010a
    return data




try:
    curses.initscr()
    window = curses.newwin(test.h+2,test.w+2,0,0)
    window.border()

    cmdwin = curses.newwin(3, 60, test.h+2, 0)

    curses.noecho()
    curses.mousemask(1)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)

    window.keypad(1)

    editbox = waxutil.EditWindow(window.subwin(test.h, test.w, 1,1))

    cmd = 0
    color = 0

    while 1:
        cmdStr =    [ "{mode} mode | color: {color}".format(mode = "Edit" if editmode else "Command", color= "green" if color else "normal")
                    ,  "{name}: {w}x{h} - {cmd:04x} - ({x},{y})".format(w = test.w, h = test.h, cmd=cmd, name = filename, x = editbox.x, y = editbox.y)
                    , "i: edit | q: quit" 
                    ]


        for i, val in enumerate(cmdStr): 
            cmdwin.addstr(i,0,val)

        window.clear()
        if drawalpha:
            for y in range(test.h):
                window.addstr(y+1, 1, ' '*test.w, curses.color_pair(2))

        window.border()
        test.draw(window,1,1)        
        if editmode:
            window.addch(editbox.y+1, editbox.x+1, '*')
        window.refresh()
        cmdwin.refresh()
        cmdwin.clear()

        if editmode:
            editmode = editbox.edit(test, color)

        else: 
            cmd = window.getch()

            if cmd == ord('i'):
                editmode = True
            elif cmd == ord('q'):
                break;
            elif cmd == ord('g'):
                color = 1-color
            elif cmd == ord('s'):
                test.save(filename)
            elif cmd == ord('l'):
                test.load(filename)
            elif cmd == ord('a'):
                drawalpha = not drawalpha

except:
    curses.endwin()
    raise
finally:
    curses.endwin()


