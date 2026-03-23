import numpy as np
import pymysql


def coon():
    con = pymysql.connect(host='localhost', user='root', password='1234', db='weibopinglun')
    cur = con.cursor()
    return con, cur


def close():
    con, cur = coon()
    cur.close()
    con.close()


def query(sql):
    con, cur = coon()
    cur.execute(sql)
    res = cur.fetchall()
    close()
    return res


def insert(sql):
    con, cur = coon()
    cur.execute(sql)
    con.commit()
    close()

def clear():
    con, cur = coon()
    cur.execute('DELETE FROM analysis')
    con.commit()
    close()

def login(username, password):
    sql = 'select * from user where username = "{0}" and password = "{1}" limit 0,1'.format(username, password)
    res = query(sql)
    if res == ():
        data = {
            'info': '该用户未注册，请注册后在登录'
        }
        return data
    else:
        data = {
            'userid': res[0][0],
            'info': "登录成功"
        }
        return data


def register(username, password):
    sql = 'select * from user where username = "{0}" and password = "{1}" limit 0,1'.format(username, password)
    res = query(sql)
    if res != ():
        data = {
            'info': '该用户已经注册'
        }
        return data
    else:
        sql = 'insert into user(`username`,`password`) values ("%s","%s")' % (username, password)
        insert(sql)
        data = {
            'info': "注册成功"
        }
        return data



def getecharts():
    sql = 'select * from analysis'
    res = query(sql)
    sentiment = []
    confidence = []
    positive_prob = []
    negative_prob = []
    for i in res:
        sentiment.append(i[0])
        confidence.append(i[1])
        positive_prob.append(i[2])
        negative_prob.append(i[3])

    data = {
        'sentiment' :sentiment,
        'confidence' :confidence,
        'positive_prob' :positive_prob,
        'negative_prob':negative_prob
    }
    return data


