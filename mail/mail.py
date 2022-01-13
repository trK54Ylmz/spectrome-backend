import pytz
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import abspath, dirname, join
from jinja2 import Environment, FileSystemLoader
from smtplib import SMTP, SMTP_SSL
from util.config import config


class MailSendService:
    def __init__(self):
        """
        Create an e-mail and send
        """
        self._smtp = None
        self._host = config.mail.host
        self._port = config.mail.port
        self._has_ssl = config.mail.has_ssl
        self._user = config.mail.user
        self._sender = config.mail.sender
        self._password = config.mail.password

    def _connect(self):
        """
        Connect to SMTP server
        """
        c = SMTP_SSL if self._has_ssl else SMTP

        self._smtp = c(self._host, self._port)
        self._smtp.login(self._user, self._password)

    def _close(self):
        """
        Close SMTP server connection
        """
        self._smtp.close()

    def get_template(self, name, **kwargs):
        """
        Get jinja2 template and render

        :param str name: template file name
        :return: html content
        :rtype: str
        """
        current = dirname(abspath(__file__))
        directory = join(current, 'view')
        fs = FileSystemLoader(searchpath=directory)

        # create jinja environment
        env = Environment(loader=fs)

        tm = datetime.now(tz=pytz.UTC)
        kwargs['now'] = tm.isoformat()
        if 'email' in kwargs:
            kwargs['email_encoded'] = kwargs['email'].replace('@', '[at]')

        # read and render template
        return env.get_template(name).render(**kwargs)

    def send(self, to, subject, text, html):
        """
        Send e-mail by using remote SMTP server

        :param str to: receiver e-mail address
        :param str subject: e-mail subject
        :param str text: e-mail plain text content
        :param str html: e-mail html content
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'Spectrome <{self._sender}>'
        msg['To'] = to

        # create multiple objects
        text = MIMEText(text, 'plain')
        html = MIMEText(html, 'html')

        msg.attach(text)
        msg.attach(html)

        try:
            self._connect()

            # send e-mail
            self._smtp.sendmail(self._user, to, msg.as_string())
        finally:
            self._close()
