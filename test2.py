import cx_Oracle as mysql

x_data = []
y_list=[]
date_list = []
try:
    conn = mysql.connect("seungsu", "tmdtn12", "orcl")
    cur = conn.cursor()

    # 기사시간 가져오기
    sql_select_tables = "select * from input1 " \
                        "where UPLOAD_DATE between to_date('20171120000000', 'YYYYMMDDHH24MISS') " \
                         "and to_date('20171122000000', 'YYYYMMDDHH24MISS') " \
                         "order by UPLOAD_DATE asc"
    cur.execute(sql_select_tables)

    for _data in cur.fetchall():
        data = _data[1:]
        print(data)
        x_data.append(data)
    print(x_data)




except mysql.DatabaseError as e:
    print('makeY Error : ', e)
finally:
    cur.close()
    conn.close()


