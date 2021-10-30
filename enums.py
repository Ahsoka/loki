from enum import Enum, auto


class Manufacturer(Enum):
    seagate = auto()
    samsung = auto()
    western_digital = auto()
    toshiba = auto()
    hitachi = auto()


class StorageType(Enum):
    hdd = auto()
    ssd = auto()
    hybrid = auto()
    ram = auto()


class FormFactor(Enum):
    two_point_five = auto()
    three_point_five = auto()
    usb = auto()
    other = auto()


class Contributors(Enum):
    andres = auto()
    ryan = auto()
    dylan = auto()
    jane = auto()
