# coding=utf-8
import re
from bs4 import BeautifulSoup
import requests
import time

def getpage(url1):
    time.sleep(2)
    proxies = {
        "http": None,
        "https": None,
    }
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    response = requests.get(url1, proxies=proxies,headers = headers)
    return response.text.encode('GBK', 'ignore').decode('GBk')

def judgeDetail(html):
    soup = BeautifulSoup(html, 'lxml')
    count = soup.find(class_='rating_wrap clearbox')
    print(count.text.replace('\n', ' ').replace('  ', ''))
    print(soup.find(class_='intro').text)

def judgeCommonts(html):
    soup = BeautifulSoup(html, 'lxml')
    li = soup.find_all('li', class_='comment-item')
    for i in li:
        print(i.find(class_='comment-info').contents[3]['title'])
        print(i.find(class_='short').text)
        print('-----------------')

def judgeDouban(html):
    soup = BeautifulSoup(html, 'lxml')
    tr = soup.find_all('div',class_='result')
    for i in range(0, 5):
        print(tr[i].find(class_='title').find('a').text.replace('\n', '').encode('GBK', 'ignore').decode('GBk'))
        # print(tr[i].find(class_='title').find('a')['onclick'])
        print(tr[i].find(class_='rating-info').text.replace('\n', '').encode('GBK', 'ignore').decode('GBk'))
        s = tr[i].find(class_='title').find('a')['onclick']
        l1 = []
        for i in s.split(','):
            l1.append(i)
        sid = l1[4].split(':')[1].replace(' ','')
        url_Detaildouban = 'https://book.douban.com/subject/'+str(sid)+'/'
        judgeDetail(getpage(url_Detaildouban))
        url_comments = url_Detaildouban + '/comments/'
        judgeCommonts(getpage(url_comments))
        print('###########')
        time.sleep(5)

def judgepage(html):
    soup = BeautifulSoup(html, 'lxml')
    tr = soup.find_all('strong')
    l1 = []
    for i in tr:
        try:
            pattern = re.compile('《(.*?)》')
            result1 = re.search(pattern, i.text)
            l1.append(result1.group())
        except:
            print('')
    print(l1)
    return l1
    # html_doc = str(html, 'utf-8')  # html_doc=html.decode("utf-8","ignore")
    # print(html_doc)
    # print(response.text.encode('utf-8'))
    # return response.text

if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/s?__biz=MzA3NTE5NDEzMw==&mid=2653049306&idx=1&sn=35502c7bf58b8e645efd1e78213f48cf&chksm=84a2bba0b3d532b65e0990aece377658b149ae094c7aa656f11c876cdedc73a5c119edbf35b0&mpshare=1&scene=1&srcid=0725Ul4qPAKQpbJ0Avr4vtmD#rd'
    bookList = judgepage(getpage(url))
    for item in bookList:
        url_douban = 'https://www.douban.com/search?cat=1001&q='+ str(item)
        judgeDouban(getpage(url_douban))
# url_Detaildouban = 'https://book.douban.com/subject/3879026'
# judgeDetail(getpage(url_Detaildouban))
# url_comments = 'https://book.douban.com/subject/3879026/comments/'
# getpage(url_comments)