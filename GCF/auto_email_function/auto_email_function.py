import smtplib
import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
from datetime import date
from googletrans import Translator

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDR = 'tjdrms2023@gmail.com'
APP_PASSWORD = '####'

def google_translate(text):
  google = Translator()
  result = google.translate(text, dest='en')
  return result.text

def news_crawler():
    category = {100: 'Politics', 101: 'Economics', 102: 'Social', 103: 'Life/Cultures', 104: 'World', 105: 'IT/Science'}

    news_list = []
    for field in category:
        url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=' + str(field)

        headers = {'User-Agent': '####'}
        news = requests.get(url, headers=headers)
        soup = BeautifulSoup(news.content, 'html.parser')

        li_elements = soup.find_all('li', class_='sh_item _cluster_content')

        num_articles, article_title, article_url = 0, '', ''
        # Iterate over the <li> elements and extract the URLs and titles
        for li in li_elements:
            # Extract the URL from the <a> tag
            url = li.find('a')['href']
            
            # Extract the title from the <a> tag
            title = li.find('a', class_='sh_text_headline').text

            # Extract the number of articles from the <span> tag
            number = int(li.find('span', class_='sh_head_more_icon_num').text)


            if num_articles <= number:
                num_articles, article_title, article_url = number, title, url
            
        news_list.append((category[field], article_title, article_url))

    content = ''

    for topic in news_list:
        content += topic[0] + '\n' + google_translate(topic[1]) + '\n' + topic[2] + '\n\n'

    return content

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
    msg['Subject'] = str(date.today()) + ' Breaking News Today'
    msg.set_content(news_crawler())
    msg['From'] = EMAIL_ADDR
    msg['To'] = EMAIL_ADDR

    smtp.send_message(msg)

    return 'OK'