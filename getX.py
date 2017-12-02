'''
1. DBMS에서 input tables를 join하고 word 속성만 추출
or
1. csv파일로 받아서 여러 csv 합치기
'''
import cx_Oracle as mysql
import hyperParameters as hp


# hyper-parameters
data_dim = hp.getHyparam("data_dim") #단어 수
non_word_num = hp.getHyparam("non_word_num")


# ex. getX("20171025125500", "20171025133600")
def getX(start_date, end_date):
    dataX = []
    column_list = []
    # DBMS 활용
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        #특정속성(upload_date등) 제외하고 워드 속성만 가져오기
        # Oracle1 - 속성명 받아와 UPLOAD_DATE 없애기
        sql_select_column= "select COLUMN_NAME from ALL_TAB_COLUMNS where table_name='INPUT1'"
        #cur.execute(sql_select_column)
        for column in cur.fetchall():
            column_list.append(column[0])
        column_list.remove("UPLOAD_DATE")
        #print(len(column_list))

        columns = ""
        str_conn = ", "
        for i in range(0, len(column_list)):
            if i < len(column_list):
                columns += column_list[i] + str_conn
            else:
                columns += column[i-1]
        # print(columns)
        # print(type(columns))

        sql_select_data= "select " + str(column)[2:-3] + " from INPUT1 " \
                         "where UPLOAD_DATE between to_date('" + start_date + "', 'YYYYMMDDHH24MISS') " \
                         "and to_date('" + end_date + "', 'YYYYMMDDHH24MISS') " \
                         "order by UPLOAD_DATE asc"
        # print(sql_select_data)
        # cur.execute(sql_select_data)
        # print(cur.fetchall())

        sql_select_tables = "select * from input1 " \
                            "where UPLOAD_DATE between to_date('" + start_date + "', 'YYYYMMDDHH24MISS') " \
                            "and to_date('" + end_date + "', 'YYYYMMDDHH24MISS') " \
                            "order by UPLOAD_DATE asc"
        cur.execute(sql_select_tables)

        # Oracle2 전체 다 꺼내서 맨 앞 column만 제거(첫번째 column : upload_date)
        for _data in cur.fetchall():
            data = _data[1:]
            # print(data)
            dataX.append(data)
        # print(dataX)

        # for MySQL
        # sql_set = "set @qry  = CONCAT('SELECT ', (SELECT REPLACE(GROUP_CONCAT(COLUMN_NAME), " \
        #           "'<upload_date>,', '') FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = " \
        #           "'<대상 테이블명>'AND TABLE_SCHEMA = '<seungu>'), ' FROM <input0> " \
        #           "where pcode ='" + company + "' " \
        #           "and st_date between to_date('" + start_date + "', 'YYYYMMDDHH24MISS') " + \
        #           "and to_date('" + end_date + "', 'YYYYMMDDHH24MISS') " \
        #           "order by st_date asc')"
        # print(sql_set)
        # cur.execute(sql_set)
        # print(cur.fetchall())

        # sql_check = "SELECT @qry;"
        # cur.execute(sql_check)
        # print(cur.fetchone())
        #
        # sql_prepare = "PREPARE result FROM @qry"
        # cur.execute(sql_prepare)
        #
        # sql_execute = "EXECUTE result"
        # cur.execute(sql_execute)
        # print(cur.fetchall())
        # #
        # record_list = cur.fetchall()
        #
        # #words 속성들로 행렬만들기
        # for i in range(0, len(record_list)/data_dim):
        #     _x = record_list[i*data_dim : (i+1)*data_dim]
        #     dataX.append(_x)
    except mysql.DatabaseError as e:
        print('getX Error : ', e)
    finally:
        cur.close()
        conn.close()

    return dataX

if __name__ == "__main__":
    print(getX("20171101000000", "20171122000000"))
