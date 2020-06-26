"""
发送email的模块
"""
import smtplib
from email.message import EmailMessage


class EmailSender:
    """
    邮件发送类
    """

    def __init__(self, smtp_server, sender_name, psw=None):
        """
        :param smtp_server: str smtp服务器url
        :param sender_name: str 发送邮箱
        :param psw: str 邮箱密码或授权码
        """
        self.smtp_server = smtp_server
        self.sender_name = sender_name
        self.psw = psw

    def send_email(self, subject, msg, receiver_name):
        """
        发送邮件方法
        :param subject: str 摘要
        :param msg: str 发送内容
        :param receiver_name: str 接收邮箱
        """
        email_msg = EmailMessage()
        email_msg.set_content(msg)
        email_msg['Subject'] = subject
        email_msg['From'] = self.sender_name
        email_msg['To'] = receiver_name

        s = smtplib.SMTP(self.smtp_server)
        if self.psw:
            s.login(self.sender_name, self.psw)
        s.send_message(email_msg)
        s.quit()
