import struct, re
import curses
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


class Frame():

    charMap =   { 1: unichr(0x2592)
                , 2: unichr(0x2593)
                , 3: unichr(0x2588)
                }

    deMap = {}

    def __init__(self, height = None, width = None):
        if len(self.deMap.keys()) == 0:
            for key,val in self.charMap.iteritems():
                self.deMap[val] = key
        self.lines = [{}, {}]
        self.arrays = [[],[]]
        self.length = 1
        if height != None and width != None:
            for i in range(len(self.arrays)):
                self.arrays[i] = ['\x00']*width*height

    def copy(self, src):
        self.lines = list(src.lines)
        self.arrays = list(src.arrays)
        self.length = src.length

    def decode(self, val):
        val = ord(val)&0x7F
        if val in self.charMap.keys():
            return self.charMap[val]
        return chr(val)

    def encode(self, val, green = 0):
        if val in self.deMap.keys():
            val = self.deMap[val]
        else:
            val = ord(val)
        if green == 1:
            val |= 0x80
        return chr(val)

    def transcode(self, val):
        result = chr(val).upper()
        result = self.decode(result)
        result = result.encode(code)
        return result

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
        for i in range(len(self.arrays)):
            if i == color:
                self.arrays[color][y*w+x] = self.decode(chr(val).upper())
            else:
                self.arrays[i][y*w+x] = '\x00'
            self.lines[i]= self.extractLines(self.arrays[i], w)

    def _bucketCheck(self, y, x, w, val, replace, color, search):
        if (y,x) in search:
            return False
        if x < 0 or x >= w or y < 0:
            return False
        if y*w+x >= len(self.arrays[0]):
            return False
        for i, arr in enumerate(self.arrays):
            if i == color:
                if arr[y*w+x] != replace:
                    return False
            elif arr[y*w+x] != '\x00':
                return False
        return True

    def bucket(self, y, x, w, val, color):
        replace = '\x00'
        for i, arr in enumerate(self.arrays):
            temp = arr[y*w+x]
            if temp != '\x00':
                replace = temp
                recolor = i
        if replace == '\x00':
            recolor = color 
        search = [(y,x)]
        found = True
        while found:
            found = False
            for sy,sx in search:
                for ty, tx in [(sy,sx+1),(sy,sx-1),(sy+1,sx),(sy-1,sx)]:
                    if self._bucketCheck(ty, tx, w, val, replace, recolor, search):
                        search.append((ty,tx))
                        found = True

        #Do replaces
        for ty, tx in search:
            self.write(ty, tx, w, val, color)



    def resizeArray(self, data, h, w, l, r, t, b):
        chunks = []
        while len(data) > 0:
            chunks.extend(data[l:r])
            data = data[w:]
        chunks = chunks[t*(r-l):b*(r-l)]
        return chunks

    def resize(self, h, w, l, r, t, b):
        for i in range(len(self.arrays)):
            self.arrays[i] = self.resizeArray(self.arrays[i], h, w, l, r, t, b)
            self.lines[i] = self.extractLines(self.arrays[i], r-l)
    

    def _drawLines(self, window, lines, ypos=0, xpos=0, color = 0):
        for pos, data in lines.iteritems():
            window.addstr(pos[0]+ypos, pos[1]+xpos, data, curses.color_pair(color)) 

    def draw(self, window, ypos=0, xpos=0):
        for i, l in enumerate(self.lines):
            self._drawLines(window, l, ypos, xpos, i)



 

class Image():

    def __init__(self, height = 13, width = 60):
        self.frames = []
        self.w = width
        self.h = height
        self.t = 0
        self.cFrame = 0
        self.frames.append(Frame(height, width))   
        self.unsaved = True
 
    def load(self, filename):
        self.frames = []
        with open(filename, "rb") as f:
            self.h, self.w = struct.unpack("HH", f.read(4))
            fRaw = f.read(self.w*self.h+1)
            while fRaw:
                nFrame = Frame()
                nFrame.load(fRaw, self.h, self.w)
                self.frames.append(nFrame)
                fRaw = f.read(self.w*self.h+1)
            self.unsaved = False

    def save(self, filename):
        
        with open(filename, "wb") as f:
            f.write(struct.pack("HH", self.h, self.w))
            for frame in self.frames:
                raw = frame.save(self.h, self.w)
                f.write(raw)
            self.unsaved = False

    def resize(self, l, r, t, b):
        for f in self.frames:
            f.resize(self.h, self.w, l, r, t, b)
        self.h = b-t
        self.w = r-l
        self.unsaved = True

    def incFrame(self, val):
        self.cFrame += val
        if self.cFrame < 0:
            self.cFrame += len(self.frames)
        if self.cFrame >= len(self.frames):
            self.cFrame -= len(self.frames)

    def addFrame(self, pos):
        nFrame = Frame(self.h, self.w)
        nFrame.copy(self.frames[pos])
        self.frames.insert(pos+1, nFrame)

    def tick(self, delta):
        self.t += delta
        if self.t > self.frames[self.cFrame].length/8.:
            self.t -= self.frames[self.cFrame].length/8.
            self.cFrame += 1
            if self.cFrame == len(self.frames):
                self.cFrame = 0

    def write(self, y, x, val, color=0):
        self.unsaved = True
        self.frames[self.cFrame].write(y, x, self.w, val, color)

    def bucket(self, y, x, val, color):
        self.frames[self.cFrame].bucket(y, x, self.w, val, color)

    def draw(self, window, ypos = 0, xpos = 0):
        self.frames[self.cFrame].draw(window, ypos, xpos)




