# import pymysql as mysql
#
# conn = mysql.connect(host='localhost', port=3306, user='seungsu',
#                      passwd='tmdtn12', db='seungsu', charset='utf8')  #mysql
# cur = conn.cursor()
#
# cur.execute("show databases")
# print(cur.fetchall())

import random

x_data = []
_x_date = []

for i in range(0,20):
    for j in range(0,2000):
        _x_date.append(random.randint(0,5))
    x_data.append(_x_date)

print(x_data)
