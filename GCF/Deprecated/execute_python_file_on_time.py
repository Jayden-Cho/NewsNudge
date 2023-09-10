import schedule
import time

import smtplib
# Use this lib to easily send emails with prompt
from email.message import EmailMessage
     

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDR = 'tjdrms2023@gmail.com'
APP_PASSWORD = 'dswjergpnowsylaj'

def send_email():
    # Create a SMTP object with server name and port number
    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    # Set up server connection
    smtp.ehlo()

    # Encrypt the connection for privacy issues
    smtp.starttls()

    # Login with email information
    smtp.login(EMAIL_ADDR, APP_PASSWORD)

    # Create an email object and its contents
    msg = EmailMessage()
    msg['Subject'] = 'subject'
    msg.set_content('abcde')
    msg['From'] = EMAIL_ADDR
    msg['To'] = EMAIL_ADDR

    smtp.send_message(msg)
    smtp.quit()

job = schedule.every(2).seconds.do(send_email)

day = 0

while True:
    schedule.run_pending()
    time.sleep(1)

    day += 1

    if day > 7:
        schedule.cancel_job(job)

# 위처럼 아예 function을 옮겨와봤는데, 에러 메세지는 발생하지 않았지만 코드 실행이 되지 않는듯 하다 (이메일도 안 날라옴)