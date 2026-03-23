import re
import time
import csv
from lxml import etree
from urllib.parse import quote
import requests
import locale
import  os
locale.setlocale(locale.LC_CTYPE, "chinese")


comment_number = 0

headers_com = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'cookie': 'SINAGLOBAL=3647921257273.139.1712301443535; UOR=,,cn.bing.com; ALF=1716365316; SUB=_2A25LImtUDeRhGeNO7VQT9yzEyzqIHXVoXuKcrDV8PUJbkNANLUHjkW1NTvXwMTm_deKbEUXl0wsrcgmxd5iBPF70; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh1NR9jqUGnB4_H0i_T1ZBb5JpX5KMhUgL.Fo-7SoqES0zRehq2dJLoIEXLxKMLB.-LBKBLxKqL1KnL1-qLxKML1-2L1hBLxKBLB.qLBK2LxKBLB.BLB.qt; _s_tentry=-; Apache=2139086242710.0466.1713773316646; ULV=1713773316692:5:5:1:2139086242710.0466.1713773316646:1713344594629',
}

def getArticleId(id_str):
    """
    :param id_str: 需要解密的id字符串
    :return:
    """
    url_id = "https://weibo.com/ajax/statuses/show?id={}".format(id_str)
    resp_id = requests.get(url_id, headers=headers_com)
    if resp_id is None:
        return 0
    article_id = resp_id.json()["id"]
    return article_id


def get_one_page(params, headers, writer):
    """
    :param params: get请求需要的参数，数据类型为字典
    :param headers: 请求头信息
    :param writer: csv文件写入对象
    :return: max_id：请求所需的另一个参数
    """
    url = "https://weibo.com/ajax/statuses/buildComments"
    resp = requests.get(url, headers=headers, params=params)

    try:
        data_list = resp.json()["data"]
    except:
        return

    for data in data_list:
        data_dict = {
            "Users": data["user"]["screen_name"].strip(),
            "Province": data["user"]["location"],
            "Date": data["created_at"].replace("+0800", ""),
            "Contents": data["text_raw"].strip().replace('\n', ''),
            "like_counts": data["like_counts"]
        }
        global comment_number
        comment_number = comment_number + 1
        print("已经爬到的评论数：", comment_number)
        print(
            f'昵称：{data_dict["Users"]}\n地址：{data_dict["Province"]}\n发布时间：{data_dict["Date"]}\n评论内容：{data_dict["Contents"]}\n点赞数：{data_dict["like_counts"]}')
        print("=" * 90)
        saveData(data_dict, writer)

    max_id = resp.json()["max_id"]
    if max_id:
        return max_id
    else:
        return


def get_all_data(params, headers, writer):
    """
    :param params: get请求需要的参数，数据类型为字典
    :param headers: 请求头信息
    :param writer: csv文件写入对象
    :return:
    """
    max_id = get_one_page(params, headers, writer)
    params["max_id"] = max_id
    params["count"] = 20
    while max_id:
        time.sleep(1)
        params["max_id"] = max_id
        max_id = get_one_page(params, headers, writer)


def saveData(data_dict, writer):
    """
    :param data_dict: 要保存的数据，形式为dict类型
    :param writer: csv文件写入对象
    :return:
    """
    writer.writerow(data_dict)


def spider_crawl(topic, headers):
    baseUrl = 'https://s.weibo.com/weibo?q={}&Refer=index'
    topic = '#' + topic + '#'
    fileName = topic.replace('#', '')

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(BASE_DIR, '..', 'spiders', '{}.csv'.format(fileName))

    header = ["Contents", "Province", "Date", "Users", "like_counts"]
    with open(filepath, "w", encoding="utf-8-sig",
              newline="") as f:
        writer = csv.DictWriter(f, header)
        writer.writeheader()

        url = baseUrl.format(quote(topic))

        page = 0
        pageCount = 1

        while True:
            page = page + 1
            tempUrl = url + '&page=' + str(page)
            print('-' * 36, tempUrl, '-' * 36)
            response = requests.get(tempUrl, headers=headers)
            html = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
            count = len(html.xpath('//div[@class="card-wrap"]')) - 2
            for i in range(1, count + 1):
                weibo_url = html.xpath(
                    '//div[@class="card-wrap"][' + str(
                        i) + ']/div[@class="card"]/div[1]/div[2]/div[@class="from"]/a/@href')

                if len(weibo_url) == 0:
                    continue

                url_str = '.*?com\/\d+\/(.*)\?refer_flag=\d+_'
                res = re.findall(url_str, weibo_url[0])

                weibo_id = res[0]
                weibo_uid = weibo_url[0].split('/')[3]

                headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                    "x-requested-with": "XMLHttpRequest",
                    "referer": "https://weibo.com/{}/{}".format(weibo_uid, weibo_id),
                    "cookie": 'SINAGLOBAL=3647921257273.139.1712301443535; UOR=,,cn.bing.com; ALF=1716365316; SUB=_2A25LImtUDeRhGeNO7VQT9yzEyzqIHXVoXuKcrDV8PUJbkNANLUHjkW1NTvXwMTm_deKbEUXl0wsrcgmxd5iBPF70; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh1NR9jqUGnB4_H0i_T1ZBb5JpX5KMhUgL.Fo-7SoqES0zRehq2dJLoIEXLxKMLB.-LBKBLxKqL1KnL1-qLxKML1-2L1hBLxKBLB.qLBK2LxKBLB.BLB.qt; _s_tentry=-; Apache=2139086242710.0466.1713773316646; ULV=1713773316692:5:5:1:2139086242710.0466.1713773316646:1713344594629',
                    "x-xsrf-token": "aDIwzDqvyb7sb-Qxm_dbqC63"
                }
                try:
                    id = getArticleId(weibo_id)  # 获取参数需要的真正id
                except:
                    continue

                params = {
                    'flow': 1,
                    "is_reload": 1,
                    "id": id,
                    "is_show_bulletin": 2,
                    "is_mix": 0,
                    "count": 10,
                    "uid": weibo_uid
                }

                get_all_data(params, headers, writer)

            try:
                if pageCount == 1:
                    pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a')[0].text
                    pageCount = pageCount + 1
                elif pageCount == 50:
                    print('没有下一页了')
                    break
                else:
                    pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a[2]')[0].text
                    pageCount = pageCount + 1
            except:
                print('没有下一页了')
                break
        print("数据爬取完毕。")

# 调用 spider_crawl 函数并传入所需参数
if __name__ == '__main__':
    topic=input()
    spider_crawl(topic, headers_com)
