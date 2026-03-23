import csv
import re
import os


def filter_emoji(desstr, restr=''):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


# 清洗文本的函数，移除图片、表情、视频和链接
def clean_text(text):
    # 移除图片和视频链接（这些通常由文件扩展名表明）
    text = re.sub(r'https?://\S*\.(jpg|jpeg|png|gif|svg|mp4|avi|wmv|flv)\b', '', text, flags=re.IGNORECASE)

    # 移除其他网页链接
    text = re.sub(r'https?://\S+', '', text, flags=re.IGNORECASE)
    # print(text)

    # 去掉@标记与@某人的标记
    r2 = "(@.*?)+ "
    text = re.sub(r2, '', text)
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)
    # print(text)

    # 过滤表情
    text = filter_emoji(text, restr='')
    text = re.sub(r"\[.*?\]", "", text)  # 去除表情符号
    # print(text)

    # 合并正文中过多的空格
    text = re.sub(r"\s+", "", text)

    text = text.replace("图片评论", "")
    text = text.replace("转发微博", "")
    return text


def output(fileName):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(BASE_DIR, '..', 'spiders', '{}.csv'.format(fileName))

    filepath_clean = os.path.join(BASE_DIR, '..', 'spiders', '{}cleaned.csv'.format(fileName))

    # 读取文件并清洗指定字段中的内容
    with open(filepath, 'r', encoding='utf-8-sig',
              newline='') as infile, \
            open(filepath_clean, 'w',
                 encoding='utf-8-sig', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

        # 写入表头
        writer.writeheader()
        for row in reader:
            # 对 `screen_name` 和 `text` 字段的内容进行清洗
            # row['screen_name'] = clean_text(row['screen_name'])
            row['Contents'] = clean_text(row['Contents'])
            row['Contents'] = row['Contents'].replace(',', ' ')

            if row['Users'] == '超话社区':
                row['Contents'] = ''
            # 写入清洗后的数据
            writer.writerow(row)

    print("CSV 文件中的相关字段已清洗完毕。")


if __name__ == '__main__':

    key = input()
    output(key)
