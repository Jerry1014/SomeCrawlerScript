import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from wxpy import *
from email.mime.image import MIMEImage

bot = Bot(False)

kindle = bot.mps().search('Kindle杂志公社')[0]
print('sending msg')
kindle.send('88387')
print('all done')
bot.logout()
