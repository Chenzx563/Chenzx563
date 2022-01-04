import requests
import xlwt 
from bs4 import BeautifulSoup
from collections import Counter 
import collections
import matplotlib.pyplot as plt 
from pylab import mpl 

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.size'] = 6.0

import time
import random

import jieba
from wordcloud import WordCloud 
import re

headers = {
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
    'Host': 'movie.douban.com'
}

## data needed
movie_list_english_name = []
movie_list_chinese_name = []
director_list = []
time_list = []
star_list = []
reviewNum_list = []
quote_list = []
nation_list = []
category_list = []

num = 0
for i in range(0, 10):
    link = 'https://movie.douban.com/top250?start=' + str(i * 25)#10 pages for total 250 movies
    res = requests.get(link, headers=headers, timeout=10)
    time.sleep(random.random() * 3)  #avoid being blocked of the IP address

    # res.text is the content of the crawler
    soup = BeautifulSoup(res.text, "html.parser")  #lxml is one decoding model for Beautifulsoup
    div_title_list = soup.find_all('div', class_='hd')  #find classes whose tag are hd
    div_info_list = soup.find_all('div', class_='bd')
    div_star_list = soup.find_all('div', class_='star')
    div_quote_list = soup.find_all('p', class_='quote')

    for each in div_title_list:
        #a is href link of html, and strip() is for stripping spacing at the beginning and end of a string
        movie = each.a.span.text.strip()  # 只能得到第一个字段，only get the first span of text this method
        movie_list_chinese_name.append(movie)

    # get second span by css location   
    div_title_list2 = soup.select('div.hd > a > span:nth-of-type(2)')
    for each in div_title_list2:
        movie = each.text
        # movie = movie.replace(u'\xa0', u' ')
        movie = movie.strip('\xa0/\xa0')  # strip the extra string in the english name
        movie_list_english_name.append(movie)

    for each in div_info_list:
        num += 1
        info = each.p.text.strip()
        if len(info) < 3:  # skip the information not needed
            continue

        # find the movie year
        lines = info.split('\n')  # split the info into two lines
        time_start = lines[1].find('20')
        if time_start < 0:
            time_start = lines[1].find('19')
        time_len = lines[1][time_start: time_start + 4]
        time_list.append(time_len)
        time_end = time_start + 4

        # find the director English name. some director name string strange, so drop this
        #        for i in range(len(info)):
        #            if info[i].encode( 'UTF-8' ).isalpha():
        #                break
        #        if i != len(info) - 1:
        #            start = i
        #            end = info.find('主')
        #            director = info[start : end - 3]
        #            director_list_english_name.append(director)

        # find the director name
        end = info.find('主')
        if end < 0:
            end = info.find('...')
        director = info[4: end - 3]
        director_list.append(director)

        # find the nation of the movie
        frequent = 0
        start = 0
        end = 0
        line2 = lines[1]
        for j in range(len(line2)):
            if line2[j] == '\xa0':
                frequent += 1
            if frequent == 2 and start == 0:
                start = j + 1
            if frequent == 3:
                end = j
                break
        nation = line2[start: end]
        nation_list.append(nation)

        # find the category of the movie
        frequent = 0
        start = 0
        for j in range(len(line2)):
            if line2[j] == '\xa0':
                frequent += 1
            if frequent == 4 and start == 0:
                start = j + 1
        category = line2[start: len(line2)]
        category_list.append(category)

    # find the star of each movie    
    for each in div_star_list:
        info = each.text.strip()
        star = float(info[0: 3])
        star_list.append(star)
        end = info.find('人')
        reviewNum = int(info[3: end])
        reviewNum_list.append(reviewNum)

    # find the best quote for each movie
    for each in div_quote_list:
        info = each.text.strip()
        quote_list.append(info)
    while len(quote_list)<250:
        quote_list.append(' ')

file = xlwt.Workbook()

table = file.add_sheet('sheet1', cell_overwrite_ok=True)

table.write(0, 0, "排名")
table.write(0, 1, "电影中文名")
table.write(0, 2, "电影其他名")
table.write(0, 3, "时间")
table.write(0, 4, "导演")
table.write(0, 5, "国家或地区")
table.write(0, 6, "评分")
table.write(0, 7, "评分人数")
table.write(0, 8, "电影类型")

for i in range(len(nation_list)):
    table.write(i + 1, 0, i + 1)
    table.write(i + 1, 1, movie_list_chinese_name[i])
    table.write(i + 1, 2, movie_list_english_name[i])
    table.write(i + 1, 3, time_list[i])
    table.write(i + 1, 4, director_list[i])
    table.write(i + 1, 5, nation_list[i])
    table.write(i + 1, 6, star_list[i])
    table.write(i + 1, 7, reviewNum_list[i])
    table.write(i + 1, 8, category_list[i])
    table.write(i + 1, 9, quote_list[i])

# save to xls file
file.save('豆瓣 top 250 电影爬虫抓取.xls')

# analysis nations
locations = []
for i in range(len(nation_list)):
    nations = nation_list[i].split(' ')
    for j in range(len(nations)):
        if nations[j] == '西德':
            nations[j] = '德国'
        locations.append(nations[j])

result = Counter(locations)
result_sort = sorted(result.items(), key=lambda x: x[1], reverse=True)  # order descending and by x[1]
result_sort = collections.OrderedDict(result_sort)
othervalue = 0
for i in range(10, len(result)):
    othervalue += list(result_sort.values())[i]


# draw the pie picture using matplotlib
def make_autopct(values):  # define the values formats in the pie
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.1f}%({v:d})'.format(p=pct, v=val)

    return my_autopct


values = []
labels = []
for i in range(10):
    values.append(list(result_sort.values())[i])
    labels.append(list(result_sort.keys())[i])
values.append(othervalue)
labels.append('其他地区')
plt.rcParams['savefig.dpi'] = 200  # set dpi for figure, affect the figure's size
plt.rcParams['figure.dpi'] = 200  # set dpi for figure
w, l, p = plt.pie(values, explode=[0.02 for i in range(11)], labels=labels, pctdistance=0.8,
                  radius=1, rotatelabels=True, autopct=make_autopct(values))
[t.set_rotation(315) for t in p]  # rotate the text for the labels
plt.title('豆瓣 TOP250 电影来源地', y=-0.1)
plt.show()

# analysis categories
categories = []
for i in range(len(category_list)):
    category = category_list[i].split(' ')
    for j in range(len(category)):
        categories.append(category[j])
result = Counter(categories)
result_sort = sorted(result.items(), key=lambda x: x[1], reverse=True)  # order descending and by x[1]
result_sort = collections.OrderedDict(result_sort)
othervalue = 0
for i in range(15, len(result)):
    othervalue += list(result_sort.values())[i]
# draw the pie picture using matplotlib
values = []
labels = []
for i in range(15):
    values.append(list(result_sort.values())[i])
    labels.append(list(result_sort.keys())[i])
values.append(othervalue)
labels.append('其他类型')
plt.rcParams['savefig.dpi'] = 200  # set dpi for figure, affect the figure's size
plt.rcParams['figure.dpi'] = 200  # set dpi for figure
w, l, p = plt.pie(values, explode=[0.02 for i in range(16)], labels=labels, pctdistance=0.8,
                  radius=1, rotatelabels=True, autopct=make_autopct(values))
[t.set_rotation(315) for t in p]  # rotate the text for the labels
plt.title('豆瓣 TOP250 电影种类', y=-0.1)
plt.show()

# 一些语气词和没有意义的词
del_words = ['的', ' ', '人', '就是', '一个', '被',
             '不是', '也', '最', '了', '才', '给', '要',
             '就', '让', '在', '都', '是', '与', '和',
             '不', '有', '我', '你', '能', '每个', '不会', '中', '没有',
             '这样', '那么', '不要', '如果', '来', '它', '对', '当', '比',
             '不能', '却', '一种', '而', '不过', '只有', '不得不', '再',
             '不得不', '比', '一部', '啦', '他', '像', '会', '得', '里']
all_quotes = ''.join(quote_list) 
all_quotes = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", " ", all_quotes)
words = jieba.lcut(all_quotes)
words_final = []
for i in range(len(words)):  # 去掉一些语气词，没有意义的词。
    if words[i] not in del_words:
        words_final.append(words[i])
text_result = Counter(words_final)
cloud = WordCloud(
    font_path='方正粗黑宋简体.ttf',
    background_color='white',
    width=1000,
    height=860,
    max_words=40
)

# wc = cloud.generate(words) # Its result is bad for Chinese through trying, so change mehtod to the next line is better
wc = cloud.generate_from_frequencies(text_result)
wc.to_file("Top250 词云分析.jpg")
plt.figure()
plt.imshow(wc)
plt.axis('off')
plt.title('电影代表性评论的词云分析')
plt.show()

# 评分最高的十部电影
star_dict = dict(zip(movie_list_chinese_name, star_list))
star_sort = sorted(star_dict.items(), key=lambda x: x[1], reverse=True)  # order descending and by x[1]
star_sort = collections.OrderedDict(star_sort)
values = []
labels = []
for i in range(10):
    labels.append(list(star_sort.keys())[i])
    values.append(list(star_sort.values())[i])
bar = plt.barh(range(10), width=values, color='pink',tick_label=labels)
for i, v in enumerate(values):  # 柱状图添加数字
    plt.text(v + 0.05, i - 0.1, str(v), color='blue', fontweight='bold')
plt.xlim(xmax=10, xmin=8)
plt.title('评分最高的十部电影')
plt.show()

# 评分人数最多的十部电影
review_dict = dict(zip(movie_list_chinese_name, reviewNum_list))
review_sort = sorted(review_dict.items(), key=lambda x: x[1], reverse=True)  # 排序 order descending and by x[1]
review_sort = collections.OrderedDict(review_sort)
values = []
labels = []
for i in range(10):
    labels.append(list(review_sort.keys())[i])
    values.append(list(review_sort.values())[i])
bar = plt.barh(range(10), width=values, color='red',tick_label=labels)
for i, v in enumerate(values):  # 柱状图添加数字
    plt.text(v + 10000, i - 0.1, str(v), color='blue', fontweight='bold')
plt.xlim(xmin=400000)
plt.title('评分人数最多的十部电影')
plt.show()