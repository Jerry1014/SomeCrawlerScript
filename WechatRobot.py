from wxpy import *

bot = Bot(console_qr=1)

kindle = bot.mps().search('Kindle杂志公社')[0]
print('sending msg')
kindle.send('88387')
print('all done')
bot.logout()
