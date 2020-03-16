import pathlib
import time
from datetime import datetime
class Logger:
    def __init__(self):
        filepath = pathlib.Path().absolute() / "lastest.log"
        self.file = open(filepath,"w")

    def log(self, str):
        self.file.writelines("[{}]: {}\n".format(datetime.now().strftime("%H:%M:%S"), str))

    def close(self):
        self.file.close()

logger = Logger()
logger.log("Logger enabled")