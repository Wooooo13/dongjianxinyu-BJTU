import requests
from datetime import datetime
from urllib.parse import quote
import csv
import os
import openpyxl as op
# import pinglun


def hot_search():
    url = 'https://weibo.com/ajax/side/hotSearch'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()['data']


def getdic(num):
    data = hot_search()
    result = []
    if not data:
        print('获取微博热搜榜失败')
        return
    date = datetime.now().strftime('微博热搜榜 %Y年%m月%d日 %H:%M')
    print(date)
    for i, rs in enumerate(data['realtime'][:num], 1):
        title = rs['word']
        raw_hot = rs['num']
        cate = rs.get('category', ' ').split(',')[0]
        link = f"https://s.weibo.com/weibo?q={quote(title)}&Refer=top"  # 使用 f-string 构建链接字符串
        try:
            label = rs['label_name']
            if label in ['新', '爆', '沸', '暖', '热', '荐']:
                label = label
            else:
                label = ' '
        except:
            label = ' '

        item = {
            'i': i,
            'title': title,
            'label': label,
            'raw_hot': raw_hot,
            'category': cate,
            'link': link  # 将链接字符串添加到字典中
        }

        print(f"{i}. {title} {label} {raw_hot} {cate} 链接：{link}")  # 使用 f-string 打印链接
        result.append(item)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(BASE_DIR, '微博热搜榜top50.csv')

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['i', 'title', 'label', 'raw_hot', 'category', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  # 写入表头
        for item in result:
            writer.writerow(item)  # 写入数据行

    print("数据已保存到")

    return result, date





if __name__ == '__main__':
    num = 50  # 获取热搜的数量
    getdic(num)

    # 保存数据
