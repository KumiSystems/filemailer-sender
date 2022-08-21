import smtplib


class SMTP:
    @classmethod
    def fromConfig(cls, config):
        return cls(config.getMailServer(), config.getMailUsername(), config.getMailPassword(), config.getMailSender(), config.getMailPort(), config.getMailSSL())

    def __init__(self, host, username=None, password=None, sender=None, port=None, ssl=None):
        port = 0 if port is None else port
        ssl = bool(ssl)

        smtpclass = smtplib.SMTP_SSL if ssl else smtplib.SMTP

        self.connection = smtpclass(host, port)
        self.connection.login(username, password)

        self.sender = sender

    def send_message(self, message, *args, **kwargs):
        if not message.get("From"):
            message["From"] = self.sender
        elif message["From"] == "None":
            message.replace_header("From", self.sender)

        self.connection.send_message(message, *args, **kwargs)

    def __del__(self):
        self.connection.close()