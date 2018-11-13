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
    cursor.execute(sql_insert, dict1)
    cursor.close()
    db.commit()
    db.close()


def getpage(url1):
    time.sleep(2)
    proxies = {
        "http": None,
        "https": None,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    response = requests.get(url1, proxies=proxies, headers=headers)
    # print (response.text.encode('GBK', 'ignore').decode('GBk'))
    return response.text.encode('GBK', 'ignore').decode('GBk')


def judgeDetail(html):
    dict1 = {'name': '', 'author': '', 'score': 0.0, 'scorePeople': 0, 'lijian': '', 'tuijian': '',
             'haixing': '', 'jiaocha': '', 'hencha': '', 'content': '', 'writerIntroduce': '', 'comments': ''}
    # try:
    soup = BeautifulSoup(html, 'lxml')
    try:
        dict1['name'] = soup.find(id='wrapper').find(
            'span').text.replace('\n', '').replace(' ', '')  # 书名
    except:
        dict1['name'] = ''
    try:
        dict1['author'] = soup.find(id='info').find(
            'a').text.replace('\n', '').replace(' ', '')  # 作者
    except:
        dict1['author'] = ''
    try:
        dict1['score'] = float(
            soup.find(class_='ll rating_num ').text.replace(' ', ''))  # 分数
    except:
        dict1['score'] = 0.0
    try:
        dict1['scorePeople'] = int(soup.find(class_='rating_people').text.replace(
            ' ', '').replace('人评价', ''))  # 评分人数
    except:
        dict1['scorePeople'] = 0
    try:
        dict1['lijian'] = soup.find(
            title='力荐').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n', '').replace(' ', '')
        dict1['tuijian'] = soup.find(
            title='推荐').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n', '').replace(' ', '')
        dict1['haixing'] = soup.find(
            title='还行').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n', '').replace(' ', '')
        dict1['jiaocha'] = soup.find(
            title='较差').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n', '').replace(' ', '')
        dict1['hencha'] = soup.find(
            title='很差').next_sibling.next_sibling.next_sibling.next_sibling.text.replace('\n', '').replace(' ', '')
    except:
        print()
    try:
        dict1['content'] = soup.find(class_='intro').text.replace(
            ' ', '').replace('\n', '')  # 内容简介
    except:
        dict1['content'] = ''
    try:
        dict1['writerIntroduce'] = soup.find(class_='indent ').find(
            class_='intro').text.replace('\n', '').replace(' ', '')  # 作者介绍
    except:
        dict1['writerIntroduce'] = ''
    return dict1


def judgeCommonts(html):#获取评论
    soup = BeautifulSoup(html, 'lxml')
    li = soup.find_all('li', class_='comment-item')
    string = ''
    for i in li:
        try:
            s1 = str(i.find(class_='comment-vote').text.replace(' ',
                                                                '').replace('\n', ' '))
            s2 = str(i.find(class_='comment-info').contents[3]['title'])
            string += s1 + '$$$' + s2 + '$$'
        except:
            continue
        s3 = str(i.find(class_='short').text)
        string += s3 + '///'
    return string

def judgeBooklist(source_list):#对比书单狗的书单与库中比对
    l = []
    soup = BeautifulSoup(open('html.txt',encoding='utf-8'), 'lxml')
    a = soup.find('div',class_ = 'rich_media_content ').find_all('a')
    for i in a:
        source = '书单来了|' + str(i.text)
        if source not in source_list:
            l.append(i['href'])
    return l

def judgeDouban(html):
    global title
    global source
    global url
    soup = BeautifulSoup(html, 'lxml')
    tr = soup.find_all('div', class_='result')
    for i in range(0, 1):
        try:
            s = tr[i].find(class_='title').find('a')['onclick']
            l1 = []
            for i in s.split(','):
                l1.append(i)
            sid = l1[4].split(':')[1].replace(' ', '')
            url_Detaildouban = 'https://book.douban.com/subject/' + \
                str(sid) + '/'
            print(url_Detaildouban)
            dict1 = judgeDetail(getpage(url_Detaildouban))
            url_comments = url_Detaildouban + '/comments/'
            commonent = judgeCommonts(getpage(url_comments))
            dict1['comments'] = commonent
            dict1['title'] = title
            dict1['source'] = source
            dict1['url'] = url
            # print(dict1)
            time.sleep(5)
            return dict1
        except:
            return None


def getBookname():
    db = pymysql.connect("localhost", "root", "123456", "mydata")
    cursor = db.cursor()
    cursor.execute("select name from booklist")
    results = cursor.fetchall()
    new = []
    for row in results:
        new.append(row[0])
    new = list(set(new))
    cursor.close()
    db.commit()
    db.close()
    return new

def getBookSource():
    db = pymysql.connect("localhost", "root", "123456", "mydata")
    cursor = db.cursor()
    cursor.execute("select sourceTitle from booklist")
    results = cursor.fetchall()
    new = []
    for row in results:
        new.append(row[0])
    new = list(set(new))
    cursor.close()
    db.commit()
    db.close()
    # print(new)
    return new


def judgepage(html):
    global title
    global source
    l1 = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find(class_='rich_media_title').text.replace(
            '\n', '').replace(' ', '')
        source = soup.find(id='js_name').text.replace('\n', '').replace(' ', '')
        pattern = re.compile('《(.*?)》')
        result1 = re.findall(pattern, soup.text.encode(
            'GBK', 'ignore').decode('GBk'))
        for item in result1:
            if item not in l1:
                l1.append("".join(item.replace('/n', '').replace(' ', '')))
    finally:
        return l1




global url
global title
global source

def start():
    global url
    public_source = ['国家地理', '华尔街日报','纽约时报书评','学校图书馆期刊','赫芬顿邮报', '经济学人', '时代周刊', '华盛顿邮报', '星期日泰晤士报', '纽约时报', '宪法', '克雷恩芝加哥商业杂志', '华尔街', '财富',
                     '福布斯',
                     '卫报', '泰晤士报', '译文经典系列14本', '译文名著文库8本', '知乎「盐」系列', '上海译文出版社-译文名著精选系列75本', '出版人周刊', '华尔街日报', '人民日报',
                     '南方日报', '新京报', '亚洲周刊', '商业周刊', '金融时报', '洛杉矶时报', '出版人周刊', '华盛顿时报', '图书馆杂志']
    url_list = [
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655440922&idx=1&sn=b8345b022042b1e9fa40ccd07b193cb5&chksm=80aa5c3bb7ddd52d84d622f7be16a559655ebd4907564637e31e3c5ba9f55220c3e59fbd3589&scene=0#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655440940&idx=1&sn=75f38d6547154d4a0a002169380e6863&chksm=80aa5c0db7ddd51ba6154b632316e7d31a749a2b6003e81bcc9d7d0dca65bd41e8fb46264781&scene=0#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655440955&idx=1&sn=4caaaa7142cc881ec903fe999f8bc01e&chksm=80aa5c1ab7ddd50c025173f1f6d75435f7eafff6836dbdee291247ce4490ae0e382ded5c4ef3&scene=0#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441703&idx=1&sn=8378d00f3c8a192baa9c398ca0fb11df&chksm=80aa5f06b7ddd6102c3a47a4598eb6c247043185d5f6fece57b66f1f909c32a45f4779826f0a&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441670&idx=1&sn=5bbca34a99593e3d42af676d751868d3&chksm=80aa5f27b7ddd6313016eccb8a49dc4b9b11abbb5ff696a265f76eee0d01df73a89c61068cdb&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441601&idx=1&sn=22649484d75d3e83ad2ca84cf9233c21&chksm=80aa5ee0b7ddd7f688fc3f89d6d42615b38356e3f1ba493de33b9d6913bf115d00cfdf1b9a96&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441561&idx=1&sn=7c2675b5cdac7d0353c15e3eb48dff90&chksm=80aa5eb8b7ddd7aefe73a6660a77d3dbcff69404b02a636859be7f2559e1829785505c43bfd1&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441484&idx=1&sn=811e05b90aa3a32aeecc0d70e542248e&chksm=80aa5e6db7ddd77b3f90aaea0e1af263b58d763d815cfbcffd2408799c74aa325783c078ddf6&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441427&idx=1&sn=285a8c74f8c32568cbef70a003469613&chksm=80aa5e32b7ddd724e4ac06ab4b77684c6b25a9f980267fd9b67ee2c3c2da393a6597588de0b6&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441388&idx=1&sn=49638b9a00e570d24459c0fe20aee88d&chksm=80aa5dcdb7ddd4dbf4986aa472892e40bdfcd6f69e133e6b864b8dc8a18786be0a470da2072e&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441314&idx=1&sn=2d6128e271a4f5f6c4cbfba59cc55cfb&chksm=80aa5d83b7ddd495e7b0b835a5cf78b312ee127f670f065fb751eb2e86f8266cc78f0debd3ee&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441292&idx=1&sn=3d8afd947595b76701f77d7bbd6f4f83&chksm=80aa5dadb7ddd4bb34aea7f9ba458b142b4a0acdc2ad975135fe5e80feb705ff0ebc826c05e0&scene=0&xtrack=1#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441274&idx=1&sn=a92a5782f6dabc08daec6fd6b8fb5ead&chksm=80aa5d5bb7ddd44d2183a8800279826126bd2fbcb324c30f79e57e1c4dd329edcca794146f46&scene=0#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441220&idx=1&sn=bfa04894929b53acbdcdfa6eae71244e&chksm=80aa5d65b7ddd473ee77a3cd4eef3db85e100366e28e9f453cfa952f36cbeb16323ccb0a80b1&scene=0#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441082&idx=1&sn=6c90848e810034ee067f0eaf44858308&chksm=80aa5c9bb7ddd58ddad8fcfa312fc9416a7a7790717e15437bcabe624b1bbb562089b286ffa6&scene=0#rd',
        'https://mp.weixin.qq.com/s?__biz=MzAwNTczMzcxMA==&mid=2655441013&idx=1&sn=932d8e3dd9266033fd9b943545cc3695&chksm=80aa5c54b7ddd5427a0c92f990f3bcc2284db2ab221738923b2625f6a8ebb98a46b49cf708d7&scene=0#rd',

        ]
    while url_list:
        dbBooklist = getBookname()
        url = url_list.pop()
        bookList = judgepage(getpage(url))
        if len(bookList)!=0:
            print(bookList)
            while bookList:
                item = "".join(bookList.pop()).replace(' ', '')
                print('last:', len(bookList))
                if item not in dbBooklist and item not in public_source:
                    print(item)
                    time.sleep(2)
                    url_douban = 'https://www.douban.com/search?cat=1001&q=' + \
                                 str(item)
                    info_detail = judgeDouban(getpage(url_douban))
                    if info_detail != None:
                        if info_detail['name'] not in dbBooklist:
                            sql(info_detail)
                            print(info_detail)
                            print('################')
                        else:
                            print(info_detail['name'], 'in db')
                    else:
                        print('no found')
                else:
                    print('in db', item)
            print('------------------')
        else:continue


if __name__ == '__main__':
    # source_list = getBookSource()
    # url_list = judgeBooklist(source_list)
    start()