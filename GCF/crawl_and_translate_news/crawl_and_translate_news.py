import os
import tempfile 
import pandas as pd
from google.cloud import storage
from datetime import datetime, timezone, timedelta
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator

huggingface_API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
huggingface_headers = {"Authorization": "####"}

def clean_text(text):
    # Remove clauses like [헤럴드경제=신현주 기자]
    text = re.sub(r'\[[^\]]+\]', '', text)
    
    # Remove newlines, backslashes, and multiple spaces
    text = text.replace('\n', ' ').replace('\\', '')
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading and trailing spaces
    cleaned_text = text.strip()
    
    return cleaned_text

def get_body_content(URL):
    headers = {'User-Agent': '####'}
    news = requests.get(URL, headers=headers)
    soup = BeautifulSoup(news.content, 'html.parser')

    news_element = soup.find('article', class_='go_trans _article_content')

    if news_element:
        tags_to_extract = ['strong', 'em', 'b', 'td']

        for tag in tags_to_extract:
            for elem in news_element.find_all(tag):
                elem.extract()            

        body = news_element.get_text(separator='\n')
        return clean_text(body)

    else:
        return 'News content not found.'
    
def google_translate(text):
    google = Translator()
    result = google.translate(text, dest='en')
    return result.text

def distilbart_summarize(text, translate='google'):
    if translate == 'google':
        text = google_translate(text)
    response = requests.post(huggingface_API_URL, headers=huggingface_headers, json={"inputs": text,})
    return response.json()[0]['summary_text']

def crawl_and_translate_news():
    category = {100: 'Politics', 101: 'Economics', 102: 'Social', 103: 'Life/Cultures', 104: 'World', 105: 'IT/Science'}

    print('Crawling started.')
    news_data = []
    for field in category:
        url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=' + str(field)

        headers = {'User-Agent': '####'}
        news = requests.get(url, headers=headers)
        soup = BeautifulSoup(news.content, 'html.parser')

        li_elements = soup.find_all('li', class_='sh_item _cluster_content')

        max_articles, max_title, max_body, max_url = 0, '', '', ''
        # Iterate over the <li> elements and extract the URLs and titles
        for li in li_elements:
            url = li.find('a')['href']
            title = li.find('a', class_='sh_text_headline').text
            number = int(li.find('span', class_='sh_head_more_icon_num').text)

            if number > max_articles:
                max_articles, max_title, max_url = number, title, url

        korean_time = (datetime.now(timezone(timedelta(hours=9)))).strftime('%Y-%m-%d')        
            
        max_body = get_body_content(max_url)
        news_data.append({'date':korean_time, 'category': category[field], 'url': max_url, 'title': max_title, 'body': max_body})

    df = pd.DataFrame(news_data)

    # Encode the Korean text before saving to DataFrame
    df['title'] = df['title'].apply(lambda text: text.encode('utf-8').decode('utf-8'))
    df['body'] = df['body'].apply(lambda text: text.encode('utf-8').decode('utf-8'))    

    df.index = [f'N{i}' for i in range(len(df))] #후에는 마지막 인덱스 보고 거기에 1 더하는 걸로 변경.
    df.reset_index(inplace=True)

    print('Translation started.')
    df['title_google_translated'] = df['title'].apply(lambda text: google_translate(text))
    df['body_google_translated_distilbart_summarized'] = df['body'].apply(lambda text: distilbart_summarize(text))
    return df

def generate_tsv(request):
    print('Main function requested.')
    df = crawl_and_translate_news()

    print('Dataset ready to go.')
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    tsv_content = df.to_csv(sep='\t', index=False, encoding='utf-8')
    temp_file.write(tsv_content.encode())
    temp_file.close()

    bucket_name = 'newsnudge'
    blob_name = 'news.tsv'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if blob.exists():
        # If 'news.tsv' exists already, download the existing content
        existing_content = blob.download_as_text()

        # Append the new content to the existing content
        new_content = existing_content + tsv_content
        blob.upload_from_string(new_content)
    else:
        # If 'news.tsv' doesn't exist, upload the new content as a new file
        blob.upload_from_filename(temp_file.name)

    # Remove the temporary file
    os.unlink(temp_file.name)

    return 'TSV file generated and added to "news.tsv" in Cloud Storage.'