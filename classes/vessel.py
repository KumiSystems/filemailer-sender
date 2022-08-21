from configparser import SectionProxy
from typing import Optional, Union
from pathlib import Path

from paramiko.client import SSHClient

import time


class Vessel:
    @classmethod
    def fromConfig(cls, config: SectionProxy):
        name = config.name
        host = config["Host"]
        username = config.get("Username")
        sourcedir = config.get("SourceDir")
        return cls(name, host, username, sourcedir)

    def __init__(self, name: str, host: str, username: Optional[str] = None, sourcedir: Optional[Union[str, Path]] = None):
        self.name = name
        self.host = host
        self.username = username or "filemailer"
        self.sourcedir = str(sourcedir) if sourcedir else "/var/filemailer"

        self._ssh = None
        self._sftp = None

    def connect(self):
        self._ssh = SSHClient()
        self._ssh.load_system_host_keys()

        try:
            self._ssh.connect(self.host, username=self.username)
            self._sftp = self._ssh.open_sftp()
        except Exception as e:
            raise Exception(f"Could not connect to {self.name} ({self.host}): {e}")

    def fetch(self, destination, retry=True):
        try:
            self._sftp.chdir(self.sourcedir)
            files = self._sftp.listdir()

            time.sleep(3) # Make sure write operations are complete

            for f in files:
                self._sftp.get(f, str(destination / f.split("/")[-1]))
                self._sftp.remove(f)

        except Exception as e:
            if retry:
                return self.fetch(destination, False)
            raise