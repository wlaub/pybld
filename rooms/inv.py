import game

class Room(game.Room):
    verbs = ["inv"]
    name = 'inv'
    desc = "This is not a room it is your inventory. What are you doing here?"

    def inv(self, cmd):
        xpos = 0
        invStr = "         "
        for item in self.items.values():
           invStr += item.name
           xpos += 1
           if xpos == 4:
               xpos = 0
               invStr += "\n"
           else:
               invStr += " "*(15-len(item.name))
        game.say(invStr)

