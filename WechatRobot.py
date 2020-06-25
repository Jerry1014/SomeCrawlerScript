from wxpy import *

user_code = '88387'
bot = Bot(console_qr=1)

kindle = bot.mps().search('Kindle杂志公社')[0]
print('sending msg')
kindle.send(user_code)
print('all done')
bot.logout()
