import lp
import configparser
import pathlib
import re
from math import sin, pi
from time import sleep
from Logger import Logger
from dataclasses import dataclass


@dataclass
class Color:
    r: int
    g: int
    b: int


class BreathingLight:
    def __init__(self):
        self.logger = Logger()
        self.loadConfig()
        self.connect()
        profiles = self.lp.getProfiles()
        if "Breathing Light" not in profiles:
            self.lp.lock()
            self.lp.setProfile("Breathing Light")
            self.lp.unlock()

    def log(self, str):
        self.logger.log(str)

    def connect(self):
        try:
            self.host = self.config.get('General', 'host')
            self.port = self.config.getint('General', 'port')
            self.lp = lp.lightpack(self.host, self.port)
            self.lp.connect()
            self.log("Connected")
            return True
        except:
            return False

    def loadConfig(self):
        self.scriptDir = pathlib.Path().absolute()
        print(self.scriptDir)
        self.config = configparser.ConfigParser()
        self.config.read(self.scriptDir / 'Settings.ini')
        self.totalCycle = int(self.config["General"].get("CycleCount"))
        self.step = float(self.config["General"].get("ChangingStep"))/1000
        self.color = []
        sectionList = []
        for section in self.config.sections():
            if re.match(r'^Color\d+$', section):
                sectionList.append(section)

        sectionList.sort()
        for section in sectionList:
            colorConfig = self.config[section]
            r = colorConfig.get("Red")
            g = colorConfig.get("Green")
            b = colorConfig.get("Blue")
            color = Color(int(r), int(g), int(b))
            self.log("{}: {}".format(section, color))
            self.color.append(color)
        self.log("Config loaded")

    def run(self):
        self.log("Running")
        locked = False
        count = 0
        fromColor = self.color[0]
        toColor = self.color[1]
        while True:
            if re.match("Breathing Light", self.lp.getProfile()) and re.match("on", self.lp.getStatus()):
                if not locked:
                    self.log("locking")
                    self.lp.lock()
                    locked = True
                    self.log("locked: {}".format(locked))
                self.lp.setColorToAll(self.colorValue(fromColor.r, toColor.r, count), self.colorValue(
                    fromColor.g, toColor.g, count), self.colorValue(fromColor.b, toColor.b, count))
                count = count + 1
                if count == self.totalCycle:
                    count = 1
                    fromColor, toColor = toColor, fromColor
            else:
                count = 0
                if locked:
                    self.log("unlocking")
                    self.lp.unlock()
                    locked = False
                    self.log("unlocked: {}".format(locked))
            sleep(self.step)

    def colorValue(self, fromColor, toColor, cycle):
        if fromColor > toColor:  # Getting Dim
            return int((fromColor-toColor) * (1-sin(pi/2*cycle/self.totalCycle))) + toColor
        elif toColor > fromColor:  # Gettting Bright
            return int((toColor-fromColor) * sin(pi/2*cycle/self.totalCycle)) + fromColor
        else:
            return fromColor


breathinglight = BreathingLight()
breathinglight.run()
