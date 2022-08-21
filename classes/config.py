from configparser import ConfigParser
from json import loads
from pathlib import Path

import socket

from .vessel import Vessel


class Config:
    @classmethod
    def fromFile(cls, path):
        parser = ConfigParser()
        parser.read(path)
        return cls(parser)

    def __init__(self, config):
        self._config = config
        
    @property
    def vessels(self):
        out = list()

        for section in filter(lambda x: x.startswith("Vessel "), self._config.sections()):
            out.append(Vessel.fromConfig(self._config[section]))

        return out

    def getTempDir(self):
        return Path(self._config["FILEMAILER"].get("TempDir", fallback="/tmp/filemailer/"))

    def getMailServer(self):
        return self._config["FILEMAILER"].get("Server", fallback="localhost")

    def getMailPort(self):
        return int(self._config["FILEMAILER"].get("Port", fallback=0))

    def getMailSSL(self):
        return bool(int(self._config["FILEMAILER"].get("SSL", fallback=0)))

    def getMailUsername(self):
        return self._config["FILEMAILER"].get("Username")

    def getMailPassword(self):
        return self._config["FILEMAILER"].get("Password")

    def getMailSender(self):
        return self._config["FILEMAILER"].get("Sender")

    def getBCC(self):
        return loads(self._config.get("FILEMAILER", "BCC", fallback="[]"))

    def getHostname(self):
        return self._config.get("FILEMAILER", "Hostname", fallback=socket.gethostname())