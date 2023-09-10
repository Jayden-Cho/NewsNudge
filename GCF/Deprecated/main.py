import smtplib
from email.message import EmailMessage

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDR = 'tjdrms2023@gmail.com'
APP_PASSWORD = 'dswjergpnowsylaj'

def send_email(request):
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

    return 'OK'