import struct, re
import curses
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

class Frame():
    lines = [{}, {}]
    length = 1

    charMap =   { 1: unichr(0x2592)
                , 2: unichr(0x2593)
                , 3: unichr(0x2588)
                }

    deMap = {}

    def __init__(self):
        if len(self.deMap.keys()) == 0:
            for key,val in self.charMap.iteritems():
                self.deMap[val] = key

    def decode(self, val):
        val = ord(val)&0x7F
        if val in self.charMap.keys():
            return self.charMap[val]
        return chr(val)

    def encode(self, val, green = 0):
        if val in self.deMap.keys():
            val = chr(self.deMap[val])
        if green == 1:
            val |= 0x80
        return val

    def extractStrings(self, data, ypos):
        result = {}
        for m in re.finditer('[^\x00]+', data):
            result[(ypos, m.start())]=m.group().encode(code)
        return result

    def extractLines(self, data, width):
        ypos = 0
        result = {}
        while len(data) > 0:
            line = data[:width]
            data = data[width:]
            result.update(self.extractStrings(line, ypos))
            ypos += 1
        return result


    def load(self, data, height, width):
        length = struct.unpack("B", data[0])
        raw = data[1:]
        plain = ''.join([self.decode(x) if ord(x) & 0x80 == 0 else '\x00' for x in raw])
        green = ''.join([self.decode(x) if ord(x) & 0x80 != 0 else '\x00' for x in raw])

        self.lines[0] = self.extractLines(plain, width)
        self.lines[1] = self.extractLines(green, width)



    def save(self, width, height):
        raw = [['\x00']*width]*height
        for key, val in self.lines[1]:
            val = ''.join([self.encode(x) for x in val])
                


    def _drawLines(self, window, lines, ypos=0, xpos=0, color = 0):
        for pos, data in lines.iteritems():
            window.addstr(pos[0]+ypos, pos[1]+xpos, data, curses.color_pair(color)) 

    def draw(self, window, ypos=0, xpos=0):
        for i, l in enumerate(self.lines):
            self._drawLines(window, l, ypos, xpos, i)
 


