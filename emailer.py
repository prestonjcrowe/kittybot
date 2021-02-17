from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import email.utils
import smtplib
import os
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT

class Emailer:
    def __init__(self, email, password, fromStr):
        self.email = email
        self.password = password
        self.fromStr = fromStr

    def new_kitties(self, cats):
        msg = MIMEMultipart()
        msg['Subject'] = f'Kitty Bot - {len(cats)} New Kitties!'
        msg['From'] = email.utils.formataddr((self.fromStr, self.email))
        msg['To'] = email.utils.formataddr(('Kiity Bot Subscriber', self.email))
        now = datetime.now()
        dtStr = now.strftime("%d/%m/%Y %H:%M:%S")

        content = f"[{dtStr}] New Kitties Posted Today\n\n"
        for cat in cats:
            line = f'{cat["description"]}\n{cat["url"]}\n\n'
            content += line
            if cat['img_path']:
                img_data = open(cat['img_path'], 'rb').read()
                image = MIMEImage(img_data, name=os.path.basename(cat['img_path']))
                msg.attach(image)

        text = MIMEText(content)
        msg.attach(text)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465) 
        server.ehlo()  
        server.login(self.email, self.password)
        server.sendmail(self.email, self.email, msg.as_string())
        #server.sendmail(self.email, 'silversumire@gmail.com', msg.as_string())

        server.quit()

    def schedule_24_hrs(self):
        tomorrow = datetime.today() + datetime.timedelta(days=1)
        
        # Dont reschedule for the 1st and 15th - normal execution times
        if tomorrow.day != 1 and tomorrow.day != 15:
            p = Popen(['at', 'now', '+', '24', 'hours'], stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding='utf8')
            stdout_data = p.communicate(input='python scheduled_buy.py')[0]

    def get_header(self, msgType):
        now = datetime.now()
        dtStr = now.strftime("%d/%m/%Y %H:%M:%S")
        return f'[{dtStr}] KUCOIN PORTFOLIO {msgType}\n\n'

    def send_receipt(self, orderStrings):
        header = self.get_header('PURCHASE')
        content = '\n'.join(orderStrings)
        self.send_email(header + content, 'KUCOIN PORTFOLIO: RECEIPT', 'pc')

    def send_error(self, err):
        header = self.get_header('ERROR')
        content = err
        self.send_email(header + content, 'KUCOIN PORTFOLIO: ERROR', 'pc')

    def send_email(self, content, subject, to):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465) 
        server.ehlo()  
        server.login(self.email, self.password)

        msg = MIMEText(content)
        msg['To'] = email.utils.formataddr((to, self.email))
        msg['From'] = email.utils.formataddr((self.fromStr, self.email))
        msg['Subject'] = subject

        server.sendmail(self.email, self.email, msg.as_string())
        server.quit()