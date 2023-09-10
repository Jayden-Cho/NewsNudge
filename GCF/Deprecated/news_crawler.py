import requests
from bs4 import BeautifulSoup
from datetime import date

def news_crawler():
    category = {100: '정치', 101: '경제', 102: '사회', 103: '생활/문화', 104: '세계', 105: 'IT/과학'}

    news_list = []
    for field in category:
        url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=' + str(field)

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
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

    return news_list

t = news_crawler()

res = ''

for topic in t:
    res += topic[0] + ' ' + topic[1] + topic[2] + '\n\n'

print(res)
print(date.today())

# 헤드라인 뉴스에 있는 각 기사마다
# (1) 뉴스 제목, (2) 파란 숫자, (3) url을 크롤링.



'''
랭킹 카테고리에서 언론사별 많이 본 뉴스와 댓글 많은 뉴스가 제공되긴하는데..
일단 문제는 분야별 랭킹이 아니라 언론사별 랭킹이라 뉴스의 분야를 파악하기 어렵고
지금 추천에 요약까지 ML을 적용해야 하는데 랭킹 카테고리 써서 또 뉴스별 분야 classification까지 더해서
프로젝트의 complexity를 키울바에야 그냥
분야별 헤드라인 뉴스를 가져와서 쓰는게 나을 것 같다.

근데 또 분야별 헤드라인 뉴스의 다른 문제점은
계속 바뀐다(..) 특정 뉴스들의 지속적으로 떠있는게 아니라
새로고침할 때 마다 헤드라인 뉴스들이 바뀐다.

그러면 하루에 한 세번 정도 크롤링해서 그 옆에 숫자대로 sort하고 10개만 추리자.

'''