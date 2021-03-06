import struct, re, copy
import os, sys
import pdb
import curses
import locale, platform
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

if platform.system() == 'Windows':
    cMap =  { 1: unichr(176)
            , 2: unichr(177)
            , 3: unichr(178)
            }
else:
    cMap =  { 1: unichr(0x2592)
            , 2: unichr(0x2593)
            , 3: unichr(0x2588)
            }


class Frame():

    charMap = cMap

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

    def compare(self, frame):
        if self.length != frame.length:
            return False
        for arr1, arr2 in zip(self.arrays, frame.arrays):
            if arr1 != arr2:
                return False
        return True

    def copy(self):
        nFrame = Frame()
        nFrame.lines = copy.deepcopy(self.lines)
        nFrame.arrays = copy.deepcopy(self.arrays)
        nFrame.length = self.length
        return nFrame

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

    def updateLines(self, width):
        for i in range(len(self.arrays)):
            self.lines[i] = self.extractLines(self.arrays[i], width)


    def writeLines(self, lines, raw, height, width, green):
        for key, val in lines.iteritems():
            val = ''.join([self.encode(x, green) for x in val.decode(code)])
            for i, v in enumerate(val):
                raw[key[0]*width + key[1] + i] = v
        return raw


    def load(self, data, height, width):
        self.length = struct.unpack("B", data[0])[0]
        raw = data[1:]
        self.arrays[0] = [self.decode(x) if ord(x) & 0x80 == 0 else '\x00' for x in raw]
        self.arrays[1] = [self.decode(x) if ord(x) & 0x80 != 0 else '\x00' for x in raw]
        self.updateLines(width)

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
        if replace == val:
            return False
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

        return True


    def resizeArray(self, data, h, w, l, r, t, b):
        chunks = []
        padx = []
        sr = r
        if r > w:
            padx = ['\x00']*(r-w) 
            sr = w
        while len(data) > 0:
            chunks.extend(data[l:sr])
            chunks.extend(padx)
            data = data[w:]
        chunks = chunks[t*(r-l):b*(r-l)]
        if b > h:
            chunks.extend(['\x00']*(r-l)*(b-h))
        return chunks

    def resize(self, h, w, l, r, t, b):
        for i in range(len(self.arrays)):
            self.arrays[i] = self.resizeArray(self.arrays[i], h, w, l, r, t, b)
        self.updateLines(r-l)

    def paste(self, yoff, xoff, h, w, nFrame, nh, nw):
        colorCount = min(len(self.arrays), len(nFrame.arrays))
        for y in range(nh):
            for x in range(nw):
                if y < h and x < w:
                    for i in range(colorCount):
                        val = nFrame.arrays[i][y*nw+x]
                        if val != '\x00':
                            for j in range(colorCount):
                                self.arrays[j][(y+yoff)*w+(x+xoff)] = val if i == j else '\x00'
        self.updateLines(w)


    def _drawLines(self, window, lines, ypos=0, xpos=0, color = 0):
        for pos, data in lines.iteritems():
            try:
                window.addstr(pos[0]+ypos, pos[1]+xpos, data, curses.color_pair(color))
            except:
                pass

    def draw(self, window, ypos=0, xpos=0):
        for i, l in enumerate(self.lines):
            self._drawLines(window, l, ypos, xpos, i)

    


 

class Image():

    def __init__(self, h = 13, w = 60, filename = None):
        self.frames = []
        self.w = w
        self.h = h
        self.x = 0
        self.y = 0
        self.t = 0
        self.cFrame = 0
        if filename == None or not os.path.exists(filename):
            self.makeEmpty(h, w)
        else:
            self.load(filename)
        self.unsaved = True

    def makeEmpty(self, height, width):
        self.frames.append(Frame(height, width))  
 
    def markChanged(self):
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

    def copy(self):
        nImage = Image(h = self.h, w = self.w)
        nImage.frames = []
        for f in self.frames:
            nImage.frames.append(f.copy())
        nImage.cFrame = self.cFrame
        return nImage

    def resize(self, l, r, t, b):
        for f in self.frames:
            f.resize(self.h, self.w, l, r, t, b)
        self.h = b-t
        self.w = r-l
        self.markChanged()

    def incFrame(self, val):
        self.cFrame += val
        if self.cFrame < 0:
            self.cFrame += len(self.frames)
        if self.cFrame >= len(self.frames):
            self.cFrame -= len(self.frames)

    def addFrame(self):
        pos = self.cFrame
        nFrame = self.frames[pos].copy()
        self.frames.insert(pos+1, nFrame)
        self.cFrame = pos+1

    def rmFrame(self):
        pos = self.cFrame
        if len(self.frames) < 2:
            return
        dFrame = self.frames[pos]
        self.frames.remove(dFrame)
        if self.cFrame >= len(self.frames):
            self.cFrame = len(self.frames)-1 

    def tick(self):
        self.t += 1
        if self.t >= self.frames[self.cFrame].length:
            self.t -= self.frames[self.cFrame].length
            self.cFrame += 1
            if self.cFrame == len(self.frames):
                self.cFrame = 0

    def write(self, y, x, val, color=0):
        self.frames[self.cFrame].write(y, x, self.w, val, color)
        self.markChanged()

    def bucket(self, y, x, val, color):
        if self.frames[self.cFrame].bucket(y, x, self.w, val, color):
            self.markChanged()

    def frameLen(self, nLen):
        self.frames[self.cFrame].length = nLen

    def copyArea(self, l, r, t, b):
        nFrame = self.frames[self.cFrame].copy()
        nFrame.resize(self.h, self.w, l, r, t, b)
        return nFrame, b-t, r-l

    def fillArea(self, l, r, t, b, char, color):
        for x in range(l, r):
            for y in range(t, b):
                self.write(y, x, char, color)
    
    def compare(self, img):
        if len(self.frames) != len(img.frames):
            return False
        for f1, f2 in zip(self.frames, img.frames):
            if not f1.compare(f2):
                return False
        return True

    def paste(self, y, x, nFrame, nh, nw):
        self.frames[self.cFrame].paste(y, x, self.h, self.w, nFrame, nh, nw)
        self.markChanged()

    def draw(self, window, ypos = 0, xpos = 0):
        self.frames[self.cFrame].draw(window, ypos, xpos)




class History():
    
    def __init__(self, image, filename):
        self.buffer = [image]
        self.future = []
        self.filename = filename
        self.eImage = None
        self.unsaved = True
        self.lastSave = image

    def save(self):
        self.unsaved = False
        self.lastSave = self.buffer[-1]
        self.lastSave.save(self.filename)

    def load(self):
        self.unsaved=False
        self.startEdit()
        self.eImage.load(self.filename)
        self.endEdit()

    def undo(self):
        if len(self.buffer) <= 1:
            return
        fut = self.buffer.pop()
        self.future.append(fut)
        self.checkSaved()

    def redo(self):
        if len(self.future) == 0:
            return
        back = self.future.pop()
        self.buffer.append(back)
        self.checkSaved()

    def draw(self, window, ypos=0, xpos=0):
        self.buffer[-1].draw(window, ypos, xpos)

    def getImage(self):
        if self.eImage != None:
            return self.eImage
        return self.buffer[-1]

    def checkSaved(self):
        self.unsaved = True
        if self.lastSave.compare(self.buffer[-1]):
            self.unsaved = False

    def startEdit(self):
        if self.eImage == None:
            self.eImage = self.buffer[-1].copy()

    def endEdit(self):        
        if self.eImage == None:
            return
        if not self.eImage.compare(self.buffer[-1]):
            self.buffer.append(self.eImage)
        self.checkSaved()

        self.eImage = None

    def partChange(self, funcName, *args, **kwargs):
        self.startEdit()
        func = Image.__dict__[funcName]
        func(self.eImage, *args, **kwargs)

    def change(self, funcName, *args, **kwargs):
        self.partChange(funcName, *args, **kwargs)
        self.endEdit()



