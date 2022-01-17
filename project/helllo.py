import requests
from bs4 import BeautifulSoup

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.iworldtoday.com/news/articleView.html?idxno=401210',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

# 코딩 시작

title = soup.select_one("#article-view-content-div > div:nth-child(9) > figure > img")

#article-view-content-div > div:nth-child(13) > figure > img

titles = soup.select("#article-view-content-div > div")
print(title['src'])

for title in titles:
    a = title.select_one('figure > img')
    print(a)