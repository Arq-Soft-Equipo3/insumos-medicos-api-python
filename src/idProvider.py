# generate random integer values
from random import seed
from random import randint


def getID():
    return randint(0, 9999)


if __name__ == "__main__":
    getID()
