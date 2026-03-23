import json
import os
from flask import Flask, request, render_template, session, send_file,jsonify
from flask import redirect, url_for
import ppredict
import until

from graph import graph_datapre
from spiders import weibohot, pinglun_1, clean


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('authentication-login.html')
    else:
        data = request.form.get('data')
        data = json.loads(data)
        res = until.login(data['username'], data['password'])
        try:
            session['userid'] = res['userid']
            session.permanent = True
            # 登录成功后重定向到 top 页面
            return redirect(url_for('top'))
        except:
            return res


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('authentication-register.html')
    else:
        data = request.form.get('data')
        data = json.loads(data)
        res = until.register(data['username'], data['password'])
        return res


# 以上是登录和注册路由

@app.route('/top', methods=['GET', 'POST'])
def index():
    return send_file('templates/top.html')


# 首页页面

@app.route('/background.html', methods=['GET', 'POST'])
def background():
    return send_file('templates/background.html')


# 背景

@app.route('/roadmap.html', methods=['GET', 'POST'])
def roadmap():
    return render_template('roadmap.html')








@app.route('/huati.html', methods=['GET', 'POST'])
def huati():
    data, time = weibohot.getdic(15)
    return render_template('huati.html', data=data, time=time)


# 以上为话题

@app.route('/base.html', methods=['GET', 'POST'])
def base():
    return render_template('base.html')


# 可视化基础界面
@app.route('/process', methods=['GET', 'POST'])
def process():
    data = request.json
    sentence = data.get('Name', '')  # 获取前端发送的
    labels = {0: '喜欢', 1: '开心', 2: '惊讶', 3: '害怕', 4: '难过', 5: '愤怒', 6: '厌恶'}
    response = "情绪分析为：" + labels[ppredict.pre(sentence)]
    return response


@app.route('/test', methods=['GET', 'POST'])
def tab():
    labels = {0: '喜欢', 1: '开心', 2: '惊讶', 3: '害怕', 4: '难过', 5: '愤怒', 6: '厌恶'}
    key = request.args.get('data')

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR,  'spiders', '{}.csv'.format(key))
    # 判断文件是否存在
    if os.path.exists(file_path):
        comments = []

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        fil = os.path.join(BASE_DIR, 'output_data', 'clean_result.csv')

        with open(fil, 'r', encoding='utf-8') as file:
            next(file)
            reader = file.readlines()

            for row in reader:
                contents = row.split(',')[0]
                province = row.split(',')[1]
                date = row.split(',')[2]
                users = row.split(',')[3]
                k = int(row.split(',')[5])
                like_label = labels[k]
                list1 = [contents, province, date, users, like_label]
                comments.append(list1)

        return render_template('table.html', comments=comments)


    else:
        if key is None:
            return render_template('base.html')
        else:
            pinglun_1.spider_crawl(key)
            clean.output(key)
            ppredict.predict(key)

            comments = []

            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            fil = os.path.join(BASE_DIR, 'output_data', 'clean_result.csv')

            with open(fil, 'r', encoding='utf-8') as file:
                next(file)
                reader = file.readlines()

                for row in reader:
                    contents = row.split(',')[0]
                    province = row.split(',')[1]
                    date = row.split(',')[2]
                    users = row.split(',')[3]
                    k = int(row.split(',')[5])
                    like_label = labels[k]
                    list1 = [contents, province, date, users, like_label]
                    comments.append(list1)
            comments = {
                'list': comments
            }
            return render_template('table.html', comments=comments)


# 评论表单
@app.route('/download_text')
def download_text():
    # 文件路径
    file_path = 'D:\PyCharm\DongJian\output_data\clean_result.csv'
    # 发送文件
    return send_file(file_path, as_attachment=True)

@app.route('/hot')
def hot():
    weibohot.getdic(50)
    dic = {}
    dic = graph_datapre.gethot()
    datax = list(dic.keys())[:8]
    data = list(dic.values())[:8]

    return render_template('hot.html', datax=datax, data=data)


@app.route('/pie', methods=['GET', 'POST'])
def pie():
    data = []
    counts = graph_datapre.pie_leida()

    data = [
        {"value": counts['喜欢'], "name": "喜欢"},
        {"value": counts['开心'], "name": "开心"},
        {"value": counts['惊讶'], "name": "惊讶"},
        {"value": counts['害怕'], "name": "害怕"},
        {"value": counts['难过'], "name": "难过"},
        {"value": counts['愤怒'], "name": "愤怒"},
        {"value": counts['厌恶'], "name": "厌恶"},
    ]
    return render_template('pie.html', data=data)


@app.route('/leida', methods=['GET', 'POST'])
def leida():
    data = []
    cnt = graph_datapre.pie_leida()
    data = [[cnt['喜欢'], cnt['开心'], cnt['惊讶'], cnt['害怕'], cnt['难过'], cnt['愤怒'], cnt['厌恶']]]
    # print(data)
    max_value = max([max(row[:-1]) for row in data])
    return render_template('radar.html', data=data, max_v=max_value + 300 )


@app.route('/prov_counts', methods=['GET', 'POST'])
def prov_counts():
    data = graph_datapre.provcnt()
    # print(data)
    return render_template('procnts.html', data=data)


@app.route('/nwpe', methods=['GET', 'POST'])
def emomap():
    data = graph_datapre.nwpe()
    datax = data[0]
    data1 = y(datax, data[1]['喜欢'])
    data2 = y(datax, data[1]['开心'])
    data3 = y(datax, data[1]['惊讶'])
    data4 = y(datax, data[1]['害怕'])
    data5 = y(datax, data[1]['难过'])
    data6 = y(datax, data[1]['愤怒'])
    data7 = y(datax, data[1]['厌恶'])
    return render_template('nwpe.html', datax=datax, data1=data1, data2=data2, data3=data3, data4=data4,
                           data5=data5, data6=data6, data7=data7)

def y(list1, list2):
    dat = []
    for i in range(len(list1)):
        da = []
        da.append(list1[i])
        da.append(list2[i])
        dat.append(da)
    return dat

@app.route('/3d', methods=['GET', 'POST'])
def main():
    datax, datalist = graph_datapre.threed()
    # print(datax)

    return render_template('3d.html', datax=datax, data=datalist)

@app.route('/cicould', methods=['GET', 'POST'])
def cicould():

    image_path = graph_datapre.wdc()
    # 使用send_file函数发送图像文件
    return send_file(image_path, mimetype='image/png')

@app.route('/daping', methods=['GET', 'POST'])
def daping():
    data, time = weibohot.getdic(20)

    return render_template('daping.html', data=data)
# 图表可视化

@app.route('/qiyegongguan.html', methods=['GET', 'POST'])
def qiye():
    return send_file('templates/qiyegongguan.html')

@app.route('/yingdaoyulun.html', methods=['GET', 'POST'])
def yingdao():
    return send_file('templates/yingdaoyulun.html')

@app.route('/shejiaohuanjing.html', methods=['GET', 'POST'])
def shejiao():
    return send_file('templates/shejiaohuanjing.html')
# 图表可视化


if __name__ == '__main__':
    # 加载bert模型

    app.run(debug=False)
