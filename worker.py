from json import loads
from email.parser import Parser as EmailParser
from email.utils import formatdate

from classes.config import Config
from classes.smtp import SMTP


config = Config.fromFile("settings.ini")

path = config.getTempDir()
path.mkdir(exist_ok=True)

smtp = SMTP.fromConfig(config)

for vessel in config.vessels:
    try:
        vessel.connect()
        vessel.fetch(path)
    except Exception as e:
        print(f"SFTP operations failed on {vessel.host}: {e}")


for eml in sorted(filter(lambda x: x.with_suffix(".json").exists(), path.glob("*.eml")), key=lambda d: d.stat().st_mtime):
    try:
        with open(eml.resolve()) as contentfile:
            content = contentfile.read()
        with open(eml.with_suffix(".json").resolve()) as metafile:
            meta = loads(metafile.read())

        message = EmailParser().parsestr(content)
        message.add_header("Received", f"by {config.getHostname()} (Kumi Systems FileMailer); {formatdate()}")

        for bcc in config.getBCC():
            if not bcc in meta["recipients"]:
                meta["recipients"].append(bcc)

        smtp.send_message(message, from_addr=meta["sender"], to_addrs=meta["recipients"])

        eml.with_suffix(".json").unlink()
        eml.unlink()

    except Exception as e:
        print(f"Could not process file {eml.resolve()}: {e}")
