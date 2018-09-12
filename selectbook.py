# coding=utf-8
import re
from bs4 import BeautifulSoup
import requests
import time

sql_insert = "insert into booklist( name,author,score,scorePeople,star5,star4,star3,star2,star1,content,writerIntroduce,comments,sourceTitle,source,sourceUrl) values(%(name)s, %(author)s,%(score)s,%(scorePeople)s, %(lijian)s, %(tuijian)s, %(haixing)s, %(jiaocha)s, %(hencha)s, %(content)s, %(writerIntroduce)s,%(comments)s, %(title)s, %(source)s, %(url)s)"

import pymysql


def sql(dict1):
    db = pymysql.connect("localhost", "root", "123456", "mydata")
    cursor = db.cursor()
    cursor.execute(sql_insert,dict1)
    cursor.close()
    db.commit()
    db.close()

def getpage(url1):
    time.sleep(2)
    proxies = {
        "http": None,
        "https": None,
    }
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    response = requests.get(url1, proxies=proxies,headers = headers)
    # print (response.text.encode('GBK', 'ignore').decode('GBk'))
    return response.text.encode('GBK', 'ignore').decode('GBk')

def judgeDetail(html):
        dict1 = {'name':'','author':'','score':0.0,'scorePeople':0,'lijian':'','tuijian':'','haixing':'','jiaocha':'','hencha':'','content':'','writerIntroduce':'','comments':''}
    # try:
        soup = BeautifulSoup(html, 'lxml')
        try:
            dict1['name'] = soup.find(id='wrapper').find('span').text.replace('\n', '').replace(' ', '')#书名
        except:dict1['name'] = ''
        try:
            dict1['author'] = soup.find(id='info').find('a').text.replace('\n', '').replace(' ', '')  # 作者
        except:dict1['author'] = ''
        try:
            dict1['score'] = float(soup.find(class_='ll rating_num ').text.replace(' ', ''))  # 分数
        except:dict1['score'] = 0.0
        try:
            dict1['scorePeople'] = int(soup.find(class_='rating_people').text.replace(' ', '').replace('人评价',''))  # 评分人数
        except: dict1['scorePeople'] = 0
        try:
            dict1['lijian'] = soup.find(title='力荐').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n','').replace(' ','')
            dict1['tuijian'] = soup.find(title='推荐').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n','').replace(' ','')
            dict1['haixing'] = soup.find(title='还行').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n','').replace(' ','')
            dict1['jiaocha'] = soup.find(title='较差').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n','').replace(' ','')
            dict1['hencha'] = soup.find(title='很差').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n','').replace(' ','')
        except:print()
        try:
            dict1['content'] = soup.find(class_='intro').text.replace(' ', '').replace('\n', '')#内容简介
        except:dict1['content'] = ''
        try:
            dict1['writerIntroduce'] = soup.find(class_='indent ').find(class_='intro').text.replace('\n', '').replace(' ', '')#作者介绍
        except:dict1['writerIntroduce'] = ''
        return dict1
    # except:print ('no detail')

def judgeCommonts(html):
    soup = BeautifulSoup(html, 'lxml')
    li = soup.find_all('li', class_='comment-item')
    string = ''
    for i in li:
        try:
            s1 = str(i.find(class_='comment-vote').text.replace(' ','').replace('\n',' '))
            s2 = str(i.find(class_='comment-info').contents[3]['title'])
            string += s1+'$$$'+s2+'$$'
        except:
            continue
        s3 = str(i.find(class_='short').text)
        string += s3+'///'
    return string


def judgeDouban(html):
    global title
    global source
    global url
    soup = BeautifulSoup(html, 'lxml')
    tr = soup.find_all('div',class_='result')
    for i in range(0, 1):
        try:
            s = tr[i].find(class_='title').find('a')['onclick']
            l1 = []
            for i in s.split(','):
                l1.append(i)
            sid = l1[4].split(':')[1].replace(' ','')
            url_Detaildouban = 'https://book.douban.com/subject/'+str(sid)+'/'
            print(url_Detaildouban)
            dict1 = judgeDetail(getpage(url_Detaildouban))
            url_comments = url_Detaildouban + '/comments/'
            commonent = judgeCommonts(getpage(url_comments))
            dict1['comments'] = commonent
            dict1['title'] = title
            dict1['source'] = source
            dict1['url'] = url
            print(dict1)
            time.sleep(5)
            return dict1
        except :
            print('nofound')
            continue


def getBookname():
    db = pymysql.connect("localhost", "root", "123456", "mydata")
    cursor = db.cursor()
    # cursor.execute(sql_insert,dict1)
    cursor.execute("select name from booklist")
    # cur.execute("select ip,proxy from proxy_ip1_text")
    results = cursor.fetchall()
    new = []
    for row in results:
        new.append(row[0])
        # print new
    new = list(set(new))
    cursor.close()
    db.commit()
    db.close()
    return new

def judgepage(html):
    global title
    global source
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find(class_='rich_media_title').text.replace('\n', '').replace(' ', '')
    source = soup.find(id='js_name').text.replace('\n', '').replace(' ', '')
    pattern = re.compile('《(.*?)》')
    result1 = re.findall(pattern, soup.text.encode('GBK', 'ignore').decode('GBk'))
    l1 = []
    for item in result1:
        l1.append(item.replace('/n', ''))
    l1 =list(set(l1))
    print(l1)
    return l1

global url
global title
global source
if __name__ == '__main__':
    global url
    url_list = ['https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439638&idx=1&sn=89b7d8f2acb8fa337ad61b2a2bbecd2e&chksm=80aa4737b7ddce21291185be834ee606113868c4692811b74357ac2ea5e3f9d669b192dc7688&scene=0#rd','https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439657&idx=1&sn=0e09411ddf1f2149ed558379b7209e51&chksm=80aa4708b7ddce1eef41fb3260ea621dc248ee1d347bb08e66a14786483b55ef97b2e1d39387&scene=0#rd','https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439745&idx=1&sn=3fda81dbb8bd4b2c54191ba7cd9dbf92&chksm=80aa47a0b7ddceb68d6294de1efc46dcd62a6011eb3915379e80ba22a46d6f8f26f469be8714&scene=0#rd','https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439760&idx=1&sn=3d797fbdbc387a604a36c614ded191eb&chksm=80aa47b1b7ddcea7d116a49dfb6caa3455145e899c3ecd535cca45e2bcb4482364d9335eb095&scene=0#rd','https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439802&idx=1&sn=f471fa6c3b8f3ce7a40e1865bfffac4b&chksm=80aa479bb7ddce8d4b16d1fd71c33d65ad1eb574339b577be2b556135fbcd4d1979e43586c81&scene=0#rd','https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439868&idx=1&sn=804711095ebf7334689b22212ca969bc&chksm=80aa47ddb7ddcecb2899b9d39dc2e227bcdeb00fab7ca49fd7e7bd768c5ac58418157601bee7&scene=0#rd','https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655439945&idx=1&sn=b6c9359ae761303e35452780a66369f5&chksm=80aa4068b7ddc97e7367671880c1a1b0116140c9530c7625f1d0e7bb42cbecae3ae0606753bb&scene=0#rd']
    while url_list:
        dbBooklist = getBookname()
        url = url_list.pop()
        print(url)
        bookList = judgepage(getpage(url))

        for item in bookList:
                url_douban = 'https://www.douban.com/search?cat=1001&q='+ str(item)
                print(url_douban)
                if item not in dbBooklist:
                    dict1 = judgeDouban(getpage(url_douban))
                    sql(dict1)
                    print("###########")
                else:
                    print('in db', item)
        print('------------------')

# sql_insert = "insert into booklist(name) values(%(name)s)"
#  url_Detaildouban = 'https://book.douban.com/subject/3879026'
# (getpage(url_Detaildouban))
# url_comments = 'https://book.douban.com/subject/3879026/comments/'
# getpage(url_comments)
