from wxpy import *

if len(sys.argv) < 2 or sys.argv[-1] == '-l' or sys.argv[-1] == '-L':
    send_qr_to_email = None
bot = Bot(console_qr=True)

kindle = bot.mps().search('Kindle杂志公社')[0]
print('sending msg')
kindle.send('88387')
print('all done')
bot.logout()
