import struct, re
import curses
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


class Frame():
    lines = [{}, {}]
    arrays = [[],[]]
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
        data = ''.join(data)
        result = {}
        while len(data) > 0:
            line = data[:width]
            data = data[width:]
            result.update(self.extractStrings(line, ypos))
            ypos += 1
        return result

    def writeLines(self, lines, raw, height, width, green):
        for key, val in lines.iteritems():
            val = ''.join([self.encode(x, green) for x in val.decode(code)])
            for i, v in enumerate(val):
                raw[key[0]*width + key[1] + i] = v
        return raw


    def load(self, data, height, width):
        length = struct.unpack("B", data[0])
        raw = data[1:]
        self.arrays[0] = [self.decode(x) if ord(x) & 0x80 == 0 else '\x00' for x in raw]
        self.arrays[1] = [self.decode(x) if ord(x) & 0x80 != 0 else '\x00' for x in raw]

        self.lines[0] = self.extractLines(self.arrays[0], width)
        self.lines[1] = self.extractLines(self.arrays[1], width)



    def save(self,  height, width):
        raw = ['\x00']*width*height
        for i, data in enumerate(self.lines):
            raw = self.writeLines(data, raw, height, width, i)
        return struct.pack("B", self.length)+''.join(raw)

    def write(self, y, x, w, val, color):
        #This needs to be done right
        self.arrays[color][y*w+x] = self.decode(chr(val).upper())
        self.lines[color]= self.extractLines(self.arrays[color], w)


    def _drawLines(self, window, lines, ypos=0, xpos=0, color = 0):
        for pos, data in lines.iteritems():
            window.addstr(pos[0]+ypos, pos[1]+xpos, data, curses.color_pair(color)) 

    def draw(self, window, ypos=0, xpos=0):
        for i, l in enumerate(self.lines):
            self._drawLines(window, l, ypos, xpos, i)



 

class Image():

    def __init__(self, width = 60, height = 13):
        self.frames = []
        self.w = width
        self.h = height
        self.t = 0
        self.cFrame = 0
    
    def load(self, filename):
        with open(filename, "rb") as f:
            self.h, self.w = struct.unpack("HH", f.read(4))
            fRaw = f.read(self.w*self.h+1)
            while fRaw:
                nFrame = Frame()
                nFrame.load(fRaw, self.h, self.w)
                self.frames.append(nFrame)
                fRaw = f.read(self.w*self.h+1)

    def save(self, filename):
        with open(filename, "wb") as f:
            f.write(struct.pack("HH", self.h, self.w))
            for frame in self.frames:
                raw = frame.save(self.h, self.w)
                f.write(raw)


    def tick(self, delta):
        self.t += delta
        if self.t > self.frames[cFrame].length/8.:
            self.t -= self.frames[cFrame].length/8
            self.cFrame += 1
            if self.cFrame == len(self.frames):
                self.cFrame = 0

    def write(self, y, x, val, color=0):
        self.frames[self.cFrame].write(y, x, self.w, val, color)

    def draw(self, window, ypos = 0, xpos = 0):
        self.frames[self.cFrame].draw(window, ypos, xpos)




