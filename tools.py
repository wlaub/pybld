#!/usr/bin/python
import game, bldgfx
import time, sys, os
import re

def getBools(template):
    """
    Scans a template for variables set to True or False and
    asks for a value.
    """
    result = []
    for line in template.split('\n'):
        out = line
        match = re.search("(?P<name>\w+)\s*=\s*(?P<val>\w+)\s*(?P<comment>#*.*)", line)
        if match != None:
            if match.group('val') == 'True' or match.group('val') == 'False':
                default = match.group('val')
                val = raw_input('{}, {} ({}): T/F? '
                             .format( match.group('name')
                                    , match.group('comment')
                                    , default)
                                    ).strip().lower()
                if 't' in val:
                    val = 'True'
                elif 'f' in val:
                    val = 'False'
                else:
                    val = default
                out = line.replace(default, val)
                if val == default:
                    out += " #Default"
        result.append(out)

    return '\n'.join(result)

def makeFname(name):
    return 'rooms/'+name.replace(' ','_').lower()+'.py'

def makeRoom():
    """
    Makes a new room file with and empty room of the given
    name.
    """
    name = raw_input("Room name: ").strip()
    fname = makeFname(name)

    if os.path.exists(fname):
        print("Room already exists.")
        return False


    with open('templates/room','r') as f:
        template = f.read()

    template = template.replace('{name}', name)
    template = getBools(template)

    with open(fname, 'w') as f:
        f.write(template)

    return True


def makeItem():
    """
    Makes an empty item with given name and location
    """
    loc = raw_input("Default room: ").strip()
    fname = makeFname(loc)

    if not os.path.exists(fname):
        print("Room {} does not exist".format(loc))
        return False

    name = raw_input("Item name: ").strip()
    cname = name.replace(' ','').capitalize()

    with open('templates/item','r') as f:
        template = f.read()

    template = template.replace('{name}', name)\
                       .replace('{cname}', cname)\
                       .replace('{loc}', loc)
    template = getBools(template)

    with open(fname, 'a') as f:
        f.write(template)

    return True


def makeCombo():
    """
    Makes an empty combo with given name, location, and
    left/right objects.
    """
    loc = raw_input("Default room: ").strip()
    fname = makeFname(loc)

    if not os.path.exists(fname):
        print("Room {} does not exist".format(loc))
        return False

    name = raw_input("Combo name: ").strip()
    cname = name.replace(' ','').capitalize()

    left = raw_input("Left object: ").strip()
    right = raw_input("Right object: ").strip()

    with open('templates/combo','r') as f:
        template = f.read()

    template = template.replace('{name}', name)\
                       .replace('{cname}', cname)\
                       .replace('{loc}', loc)\
                       .replace('{left}', left)\
                       .replace('{right}', right)
    template = getBools(template)

    with open(fname, 'a') as f:
        f.write(template)

    return True




if __name__ == '__main__':
    while True:
        print('(R)oom, (I)tem, (C)ombo, (Q)uit')
        cmd = raw_input('> ').strip().lower()

        if cmd == 'q':
            break
        elif cmd == 'i':
            makeItem()
        elif cmd == 'r':
            makeRoom()
        elif cmd == 'c':
            makeCombo()
        else:
            print('Invalid command')





