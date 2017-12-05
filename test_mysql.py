# import pymysql as mysql
#
# conn = mysql.connect(host='localhost',user='seungsu',password='tmdtn12',
#                                         db='seungsu', charset='utf8mb4')
# cur = conn.cursor()
#
# sql_insert_tables = "insert into stock_price(st_date, pcode, price) " \
#                     "values(str_to_date('2017-12-04 15:35:00', '%Y-%m-%d %H:%i:%s'), " \
#                     "'039490', 82700)"
# print(sql_insert_tables)
# print(sql_insert_tables)
# cur.execute(sql_insert_tables)
# conn.commit()
# try:
#     sql = "show databases"
#     cur.execute(sql)
#     print(cur.fetchall())
# finally:
#     conn.close()

