import game

class Room(game.Room):
    verbs = ["inv"]
    name = 'inv'
    desc = "This is not a room it is your inventory. What are you doing here?"

    def inv(self, cmd):
        xpos = 0
        invStr = "         "
        for pos in self.items.values():
            for item in pos.values():
                if not item.hidden:
                    nameStr = item.name
                    if item.qty > 1:
                        nameStr+="({})".format(item.qty)
                    invStr += nameStr
                    xpos += 1
                    if xpos == 4:
                        xpos = 0
                        invStr += "\n"
                    else:
                        invStr += " "*(15-len(nameStr))
        game.say(invStr)

