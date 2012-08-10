import os

CYAN ='\033[1;35m'
MAGENTA ='\033[1;35m'
BLUE = '\033[1;34m'
YELLOW = '\033[1;33m'
GREEN = '\033[1;32m'
RED = '\033[1;31m'
ENDC = '\033[1;m'

class ColoredString(object):
    
    def __init__(self, v,color):
        self.v = str(v)
        self.color = color

    def len(self):
        return len(self.v)

    def ljust(self, max):
        self.v = self.v.ljust(max)
        return self.__str__()

    def __str__(self):
        if os.name != "posix":
            return self.v

        if self.color == "red":
            return RED + self.v + ENDC
        elif self.color == "blue":
            return BLUE + self.v + ENDC
        elif self.color == "green":
            return GREEN + self.v + ENDC
        elif self.color == "yellow":
            return YELLOW + self.v + ENDC
        elif self.color == "cyan":
            return CYAN + self.v + ENDC
        elif self.color == "magenta":
            return MAGENTA + self.v + ENDC

        return self.v

if __name__ == "__main__":
    aa = ColoredString("what","red")
    print aa


