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
            return None
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
        if item not in l1:
            l1.append("".join(item.replace('/n', '').replace(' ','')))
        # l1.append(item.replace('/n', ''))
    # l1 =list(set(l1))
    # print(l1)
    return l1

global url
global title
global source
if __name__ == '__main__':
    global url
    source = ['国家地理','华尔街日报', '经济学人', '时代周刊', '华盛顿邮报', '星期日泰晤士报','纽约时报','卫报','泰晤士报','译文经典系列14本','译文名著文库8本','知乎「盐」系列','上海译文出版社-译文名著精选系列75本']
    url_list = ['https://mp.weixin.qq.com/s?__biz=MzAwOTEzMTkzNw==&mid=2663324136&idx=1&sn=aa0939c713df885f9ae4886cda3d48dc&chksm=802ffb26b758723096b0fba169c222b4553d7da4878536bdb744b4fc9f51fc06e9887ebfd67d&mpshare=1&scene=1&srcid=0920t9GwvIHs7qc0MfNdd8sK#rd']
    print(source)
    while url_list:
        dbBooklist = getBookname()
        url = url_list.pop()
        # print(url)
        bookList = judgepage(getpage(url))
        for item in bookList:
            item = "".join(item).replace(' ','')
            # print('item',item)
            if item not in dbBooklist and item not in source:
            # if item  in source:
                print(item)
                url_douban = 'https://www.douban.com/search?cat=1001&q='+ str(item)
                # print(url_douban)
                if judgeDouban(getpage(url_douban)) != None:
                    dict1 = judgeDouban(getpage(url_douban))
                    sql(dict1)
                    print("###########")
                else:continue
            else:
                print('in db', item)
        print('------------------')

# sql_insert = "insert into booklist(name) values(%(name)s)"
#  url_Detaildouban = 'https://book.douban.com/subject/3879026'
# (getpage(url_Detaildouban))
# url_comments = 'https://book.douban.com/subject/3879026/comments/'
# getpage(url_comments)

