import cx_Oracle as mysql

def makeXY(company, start_date, end_date):
    x_data = []
    y_list=[]
    date_list = []
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        # 기사시간 가져오기
        sql_select_tables = "select to_char(upload_date, 'YYYYMMDDHH24MISS') " \
                            "from input0 " \
                            "where st_date between to_date('"+start_date+"', 'YYYYMMDDHH24MISS') " + \
                            "and to_date('"+end_date+"', 'YYYYMMDDHH24MISS') " \
                            "order by st_date asc"
        cur.execute(sql_select_tables)
        for date in cur.fetchall():
            date_list = date[1:-2]

        # X데이터 가져오기
        for _date in date_list:
            sql_select_tables = "select *" \ 
                                "from input0 " \
                                "where st_date between to_date('"+start_date+"', 'YYYYMMDDHH24MISS') " + \
                                "and to_date('"+end_date+"', 'YYYYMMDDHH24MISS') " \
                                "order by st_date asc"
        cur.execute(sql_select_tables)
        x_data.append(cur.fetchall()[16:-2]) #최근 60분은 y_hat이 없음

        # Y데이터 가져오기
        sql_select_tables = "select y_hat " \
                            "from stock_price " \
                            "where pcode='" + company + "' and" \
                            "st_date="
        cur.execute(sql_select_tables)
        for y_hat in cur.fetchall():
            y_list.append(str(y_hat)[1:-2])
        y_list = y_list[0:-60] #최근 60분은 y_hat이 없음

    except mysql.DatabaseError as e:
        print('makeY Error : ', e)
    finally:
        cur.close()
        conn.close()
    return y_list

print(makeXY("039490"))
