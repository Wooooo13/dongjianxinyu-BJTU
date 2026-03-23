import jieba
import wordcloud
import os
from spiders import weibohot
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(BASE_DIR, '..', 'output_data', 'clean_result.csv')

labels = {0: '喜欢', 1: '开心', 2: '惊讶', 3: '害怕', 4: '难过', 5: '愤怒', 6: '厌恶'}

pe = {'喜欢': {}, '开心': {}, '惊讶': {}, '害怕': {}, '难过': {}, '愤怒': {}, '厌恶': {}}


def isinDict(dict, tstr):
    if (tstr in dict) == True:
        dict[tstr] += 1
    else:
        dict[tstr] = 1


def emosplit(str, dict, labels):  # 统计emotion
    j = str.split(',')[5]
    k = j.split('\n')[0]
    k = int(k)
    isinDict(dict, labels[k])


def pprovince(str, dict, labels):
    j = str.split(',')[5]
    emo = j.split('\n')[0]

    prov = str.split(',')[1].split(' ')[0]
    isinDict(dict[labels[int(emo)]], prov)


def pie_leida(flname=filepath):
    counts = {'喜欢': 0, '开心': 0, '惊讶': 0, '害怕': 0, '难过': 0, '愤怒': 0, '厌恶': 0}
    if flname == '':
        flname = 'result2.csv'
    f = open(flname, mode='r', encoding='utf-8')
    flag = 0  # 跳过第一行
    for i in f.readlines():
        if flag == 1:
            emosplit(i, counts, labels)
        flag = 1
    return counts


def provcnt(flname=filepath):
    pro_data = {}
    f = open(flname, mode='r', encoding='utf-8')
    flag = 0  # 跳过第一行
    for i in f.readlines():
        if flag == 1:
            prov = i.split(',')[1].split(' ')[0]

            if prov == "北京" or prov == "重庆" or prov == "上海" or prov == "天津":
                prov += '市'
            elif prov == "其他" or prov == "海外":
                prov = prov
            elif prov == "新疆":
                prov += "维吾尔自治区"
            elif prov == "广西":
                prov += "壮族自治区"
            elif prov == "宁夏":
                prov += "回族自治区"
            elif prov == "内蒙古" or prov == "西藏":
                prov += "自治区"
            else:
                prov += '省'
            if prov in pro_data:
                pro_data[prov] += 1
            else:
                pro_data[prov] = 1
        flag = 1
    formatted_data = []

    for province, count in pro_data.items():
        formatted_data.append({'name': province, 'value': count})
    return formatted_data


def nwpe(flname=filepath):
    with open(flname, mode='r', encoding='utf-8') as f:
        flag = 0  # 跳过第一行
        for i in f.readlines():
            if flag == 1:
                pprovince(i, pe, labels)
            flag = 1  # 统计各种情绪各省有多少人(pe)

    allprovince = {}
    pe_emo = {}
    for i in pe:
        for j in pe[i]:
            if (j in allprovince) == True:
                allprovince[j] += pe[i][j]
                # cnt+=dic[i][j]
            else:
                allprovince[j] = pe[i][j]
                # cnt+=dic[i][j]

    for i in allprovince:
        pe_emo[i] = {}  # 各省各情绪人数
        for j in pe:
            pe_emo[i][j] = 0
    for i in pe:
        for j in pe[i]:
            pe_emo[j][i] += pe[i][j]

    x_gra = []
    y_gra = {}
    data = []  # 储存数据返回

    for i in pe_emo:
        # print[i]
        x_gra.append(i)
        for j in pe_emo[i]:
            # y_gra[j].append(i[j])
            if (j in y_gra) == True:
                y_gra[j].append(pe_emo[i][j] / allprovince[i])
            else:
                y_gra[j] = [pe_emo[i][j] / allprovince[i]]

    data.append(x_gra)
    data.append(y_gra)

    return data


def wdc(flname=filepath, str1=""):
    with open(flname, mode='r', encoding='utf-8') as f:
        flag = 0  # 跳过第一行
        for i in f.readlines():
            if flag == 1:
                str1 += i.split(',')[0]
            flag = 1
    ls = jieba.lcut(str1)  # 生成分词列表
    text = ' '.join(ls)  # 连接成字符串

    stopwords = ["我", "你", "她", "的", "是", "了", "在", "也", "和", "就", "都", "这", "啊啊啊"]  # 去掉不需要显示的词
    import numpy as np
    from PIL import Image
    mk = np.array(Image.open("D:\PyCharm\DongJian\graph\wdbg.png"))
    wc = wordcloud.WordCloud(font_path="msyh.ttc",
                             mask=mk,
                             width=700,
                             height=700,
                             background_color=None,
                             max_words=200,
                             stopwords=stopwords,
                             mode="RGBA")

    # msyh.ttc电脑本地字体，写可以写成绝对路径
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return "hsl(0, 100%, " + str(int(50 + 50 * random_state.rand())) + "%)"  # 随机颜色

    # 根据词频设置词云文本颜色深浅
    wc.generate(text)
    wc.recolor(color_func=color_func, random_state=np.random.RandomState(3))

    wc_img = wc.to_image()
    new_size = (800, 800)  # New size, width is 800 and height is 600
    wc_img_resized = wc_img.resize(new_size)

    wc_img_resized.save("D:\\PyCharm\\DongJian\\templates\\wdc.png")
    return "templates/wdc.png"


def threed():
    pro_data = {}
    f = open(filepath, mode='r', encoding='utf-8')
    flag = 0  # 跳过第一行
    for i in f.readlines():
        if flag == 1:
            prov = i.split(',')[1].split(' ')[0]
            if prov in pro_data:
                pro_data[prov] += 1
            else:
                pro_data[prov] = 1
        flag = 1
    formatted_data = []

    for province, count in pro_data.items():
        formatted_data.append({'name': province, 'value': count})

    sorted_data = sorted(formatted_data, key=lambda x: x['value'], reverse=True)
    sorted_names = [item['name'] for item in sorted_data[:10]]
    # print(sorted_names)
    province_emotion_likes = {name: {} for name in sorted_names}
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = file.readlines()[1:]
        for i in reader:
            prov = i.split(',')[1].split(' ')[0]
            if prov in sorted_names:
                emotion = i.split(',')[5].strip()
                if emotion not in province_emotion_likes[prov]:
                    province_emotion_likes[prov][emotion] = 0
                    like_count = int(i.split(',')[4].strip())
                    province_emotion_likes[prov][emotion] += like_count
                else:
                    like_count = int(i.split(',')[4].strip())
                    province_emotion_likes[prov][emotion] += like_count

    data_list = []
    locationmap = {sorted_names[0]: 0, sorted_names[1]: 1, sorted_names[2]: 2, sorted_names[3]: 3, sorted_names[4]: 4,
                   sorted_names[5]: 5, sorted_names[6]: 6, sorted_names[7]: 7, sorted_names[8]: 8, sorted_names[9]: 9}
    for province, emotions in province_emotion_likes.items():
        for emotion, likes in emotions.items():
            data_list.append([locationmap[province], int(emotion), likes])

    # print(data_list)

    # print(province_emotion_likes)
    return sorted_names, data_list


def gethot():
    csv_file_path = 'D:\PyCharm\DongJian\spiders\微博热搜榜top50.csv'

    category_raw_hot_dict = {}

    with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)

        for row in reader:
            category = row.get('category', '').strip()
            raw_hot = row.get('raw_hot', '').strip()

            if category and raw_hot:
                # 将 raw_hot 转换为整数，如果它是字符串的话
                raw_hot = int(raw_hot)

                # 将 category 作为键，raw_hot 作为值，存储到字典中
                if category in category_raw_hot_dict:
                    category_raw_hot_dict[category] += raw_hot
                else:
                    category_raw_hot_dict[category] = raw_hot


        return category_raw_hot_dict



if __name__ == '__main__':
    # 加载bert模型
    gethot()
