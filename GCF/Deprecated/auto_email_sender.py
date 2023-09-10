import smtplib
from email.message import EmailMessage
import schedule
import time

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

job = schedule.every(10).seconds.do(send_email)

while True:
    schedule.run_pending()
    time.sleep(1)    

# # When attachment is needed:
# file = './test.csv'
# fp = open(file, 'rb')
# file_data = fp.read()
# msg.add_attachment(file_data, maintype='text', subtype='plain', filename='test.csv')

# # When html format is needed:
# html = f"""
# <html>
#     <body>
#         <h1>{subject}<h1>
#         <p>{body}</p>
#     </body>
# </html>
# """
# msg.add_alternative(html, subtype='html')
# import ssl
# context = ssl.create_default_context()