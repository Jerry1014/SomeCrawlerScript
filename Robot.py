import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from wxpy import *
from email.mime.image import MIMEImage


def send_qr_to_email(uuid, status, qrcode):
    if status == '0':
        print('sending email')
        send_str = '<html><body>'
        send_str += '<img src="cid:image1" alt="image1" align="center" width=30% >'
        send_str += '</body></html>'
        qr_image = MIMEImage(qrcode)
        qr_image.add_header('Content-ID', 'image1')

        msg = MIMEMultipart()
        msg.attach(MIMEText(send_str, _subtype='html', _charset='utf8'))
        msg.attach(qr_image)

        msg['From'] = formataddr(["微信签到", '13322468550@163.com'])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["主人", '757320383@qq.com'])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "微信登录"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP('smtp.163.com', 25)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login('13322468550@163.com', '')  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail('13322468550@163.com', '757320383@qq.com', msg.as_string())


if sys.argv[-1] == '-l' or sys.argv[-1] == '-L':
    send_qr_to_email = None
bot = Bot(True, qr_callback=send_qr_to_email)

kindle = bot.mps().search('Kindle杂志公社')[0]
print('sending msg')
kindle.send('88387')
print('all donw')
