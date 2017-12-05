'''
hyper-parameter = limitTimePoint(0~100%), decideY(0.0~1.0)
0. 원하는 시간의 주식 가격 데이터를 가져오는 함수(getPrice(company, date)) 만들기
1. 한계시간 구하기 (limitTime)
    1.1 기사 시간에 따른 주식데이터 가져오기(매1분, 1시간까지)(price_everyMin[])
    1.2 기사 시점 price * 1.01 을 지나가는 시점 저장 5개(eachAscTimes[])
    1.3 저장된 시점들의 분포도를 그리고 limitTimePoint 체크
2. 발행시점 이후 한계시간 이내 1분당 주식데이터 가져오기(price_everyMin[])
3. 발행시점 가격과 비교하여 평균 구하기(meanPoint)
    3.1 meanPoint > decideY이면 Y = 1, 아니면 Y = 0
* histogram, plot 그리기
'''

import numpy as np
import hyperParameters as hp
import pymysql as mysql

#hyper-parameters
limitTimePoint=float(hp.getHyparam("limitTimePoint")) #상승시점 분포 기준
decideY=float(hp.getHyparam("decideY")) #기사 발행시점 이후 limitTime 이내 판매가 이상 유지시간
data_dim = hp.getHyparam("data_dim") #단어 수
non_word_num = hp.getHyparam("non_word_num")

# savePrice()에 의해 DB에 저장된 [date, price]정보를 가져와 반환
# ex. price= getPrice("039490", "20171025125500", "20171025133600")
def getPrice(company, start_date, end_date):
    price=[]
    try:
        conn = mysql.connect(host='localhost',user='seungsu',password='tmdtn12',
                                        db='seungsu', charset='utf8')
        cur = conn.cursor()

        sql_select_tables = "select price " \
                            "from stock_price " \
                            "where pcode='" + company + "' "\
                            "and st_date between STR_TO_DATE('"+start_date+"', '%Y-%m-%d %H:%i:%s') " + \
                            "and STR_TO_DATE('"+end_date+"', '%Y-%m-%d %H:%i:%s') " \
                            "order by st_date asc"
        #print(sql_select_tables)
        cur.execute(sql_select_tables)
        # price=cur.fetchall()[0]
        # price=str(price)[1:-2]
        #
        for _price in cur.fetchall():
            price.append(str(_price)[1:-2])
    except mysql.DatabaseError as e:
        print('getPrice Error : ', e)
    finally:
        cur.close()
        conn.close()
    return price

# 단기매매 한계시간 산출
def getLimitTime(company):
    stnd_price= []
    eachAscTimes = []

    try:
        conn = mysql.connect(host='localhost',user='seungsu',password='tmdtn12',
                                        db='seungsu', charset='utf8')
        cur = conn.cursor()

        '''매번 DB에 접근하여 느림
        #기사들의 date 가져오기
        sql_select_tables = "select to_char(st_date, '$Y%m%d%H%i%s') " \
                            "from stock_price"

        cur.execute(sql_select_tables)
        for date in cur.fetchall():
            date_list.append(str(date)[2:-3])

        #각 date 이후 60분 이내 매1분 주가 가져와서 price_everyMin 만들기
        for date in date_list[60:-60]:
            date = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
            date_60 = date + datetime.timedelta(hours=1)
            price_everyMin.append(getPrice(company, date.strftime('%Y%m%d%H%M%S'), date_60.strftime('%Y%m%d%H%M%S')))
        '''

        #전체 분봉 가격리스트를 가져와 60개씩 자름
        price_list=[]
        price_list2=[]
        sql_select_tables = "select price " \
                            "from stock_price " \
                            "where pcode='"+company+"' " \
                            "order by st_date asc"
        cur.execute(sql_select_tables)
        for _price in cur.fetchall():
            price_list.append(str(_price)[1:-2])
        for i in range(0, len(price_list)-60):
            price_list2.append(price_list[i:60+i])

        #각 뉴스별 기준가격 stnd_price 만들기
        for i in range(0, len(price_list2)):
            stnd_price.append(price_list2[i][0])

        #상승시점들 저장
        for i in range(0, len(stnd_price)):
            for j in range(0, 60):
                if int(price_list2[i][j]) >= int(stnd_price[i]) * 1.01:
                    eachAscTimes.append(j)
        print(eachAscTimes)
        #한계시간 구하기
        limitTime = np.array(eachAscTimes)
        limitTime = np.percentile(eachAscTimes, limitTimePoint)

    except mysql.DatabaseError as e:
        print('getLimitTime Error : ', e)
    finally:
        cur.close()
        conn.close()
    return limitTime

# 해당 종목의 y_hat을 산출하여 DB에 저장
def makeY(company):
    stnd_price=[]
    date_list = []
    y_list = []

    try:
        conn = mysql.connect(host='localhost',user='seungsu',password='tmdtn12',
                                        db='seungsu', charset='utf8')
        cur = conn.cursor()

        #날짜정보 가져오기
        sql_select_tables = "select CAST(st_date as char) " \
                            "from stock_price " \
                            "where pcode='" + company + \
                            "' order by st_date asc"
        cur.execute(sql_select_tables)
        for date in cur.fetchall():
            date_list.append(str(date)[2:-3])


        #가격정보 가져오기
        price_list=[]
        price_list2=[]
        sql_select_tables = "select price " \
                            "from stock_price " \
                            "where pcode='"+company+\
                            "' order by st_date asc"
        cur.execute(sql_select_tables)
        for _price in cur.fetchall():
            price_list.append(str(_price)[1:-2])
        for i in range(0, len(price_list)-60):
            price_list2.append(price_list[i:60+i])

        #각 뉴스별 기준가격 stnd_price 만들기
        for i in range(0, len(price_list2)):
            stnd_price.append(price_list2[i][0])

        #중간확인 - 각 리스트의 개수
        #print(len(price_list), len(price_list2), len(stnd_price), len(date_list))

        #상승/하강 확인
        for i in range(0, len(stnd_price)):
            k = 0
            for j in range(0, 60):
                if int(price_list2[i][j]) >= int(stnd_price[i])*1.005:
                    k += 1
            meanPoint = (k/60)
            if (meanPoint >= decideY):
                y_hat = 1
            elif (meanPoint < decideY):
                y_hat = 0
            y_list.append(y_hat)
        y_list=np.array(y_list)
        print(company +"사 "+str(len(y_list))+"개 Y데이터 분석")
        print(np.mean(y_list))
        #날짜에 맞는 y_hat 값 넣기

        #todo 최근 y_hat 저장날자 구하여 해당날짜 까지만 수행
        for i in range(0, len(date_list)-60):
            _date = str(date_list[i])
            _y_hat = str(y_list[i])
            sql_update_tables = "update stock_price " \
                                "set y_hat=" + _y_hat + " " \
                                "where st_date=STR_TO_DATE('"+_date+"','%Y-%m-%d %H:%i:%s')"
            cur.execute(sql_update_tables)
        conn.commit()

        # temp = []
        # for i in range(0, len(date_list)-60):
        #     temp.append((int(y_list[i]), date_list[i]))
        # sql_update_tables = "update stock_price set y_hat=:1 where st_date=to_date(':2','YYYYMMDDHH24MISS')"
        # cur.executemany("update stock_price set y_hat=:1 where st_date=to_date(':2','YYYYMMDDHH24MISS')", temp)
        # conn.commit()

        # executemany로 실행
        # for i in range(0, len(date_list)-60):
        #     executemany.append((str(date_list[i]), str(y_list[i])))
        # sql_update_tables = "update stock_price set y_hat=:1 " \
        #                     "where st_date=to_date(':2','YYYYMMDDHH24MISS')"
        # cur.executemany(sql_update_tables, executemany)
        # conn.commit()
    except mysql.DatabaseError as e:
        print('makeY Error : ', e)
    finally:
        cur.close()
        conn.close()

# DB에서 원하는 기간의 y_hat을 선택하여 반환
def getY(company, start_date, end_date):
    dataY = []

    # date 형변환
    start_date = start_date[:-10]+"-"+start_date[-10:-8]+"-"+start_date[-8:-6]+" "\
                 +start_date[-6:-4]+":"+start_date[-4:-2]+":"+start_date[-2:]
    end_date = end_date[:-10]+"-"+end_date[-10:-8]+"-"+end_date[-8:-6]+" "\
               +end_date[-6:-4]+":"+end_date[-4:-2]+":"+end_date[-2:]

    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        sql_select_Yhat = "select y_hat " \
                          "from stock_price " \
                          "where pcode='" + company + "' " \
                          "and st_date between STR_TO_DATE('" + start_date + "', '%Y-%m-%d %H:%i:%s') " \
                          "and STR_TO_DATE('" + end_date + "', '%Y-%m-%d %H:%i:%s') " \
                          "order by st_date asc"
        cur.execute(sql_select_Yhat)
        for item in cur.fetchall():
            dataY.append(item[0])

    except mysql.DatabaseError as e:
        print('getY Error : ', e)
    finally:
        cur.close()
        conn.close()
    return dataY

# DB에서 원하는 기간의 데이터를 불러와 반환
# return: dataX, dataY
def getData(company, start_date, end_date):
    # ex. getX("20171025125500", "20171025133600")
    dataX = []
    dataY = []
    date_list = []

    # DBMS 활용
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        ''' for Oracle'''
        # #특정속성(upload_date등) 제외하고 워드 속성만 가져오기
        # # Oracle1 - 속성명 받아와 UPLOAD_DATE 없애기
        # sql_select_column= "select COLUMN_NAME from ALL_TAB_COLUMNS where table_name='INPUT1'"
        # #cur.execute(sql_select_column)
        # for column in cur.fetchall():
        #     column_list.append(column[0])
        # column_list.remove("UPLOAD_DATE")
        # #print(len(column_list))
        #
        # columns = ""
        # str_conn = ", "
        # for i in range(0, len(column_list)):
        #     if i < len(column_list):
        #         columns += column_list[i] + str_conn
        #     else:
        #         columns += column[i-1]
        # # print(columns)
        # # print(type(columns))
        #
        # sql_select_data= "select " + str(column)[2:-3] + " from INPUT1 " \
        #                  "where UPLOAD_DATE between to_date('" + start_date + "', 'YYYYMMDDHH24MISS') " \
        #                  "and to_date('" + end_date + "', 'YYYYMMDDHH24MISS') " \
        #                  "order by UPLOAD_DATE asc"
        # print(sql_select_data)
        # cur.execute(sql_select_data)
        # print(cur.fetchall())

        ''' for MySQL'''
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

        # x데이터 호출

        # date 형변환
        start_date = start_date[:-10]+"-"+start_date[-10:-8]+"-"+start_date[-8:-6]+" "\
                     +start_date[-6:-4]+":"+start_date[-4:-2]+":"+start_date[-2:]
        end_date = end_date[:-10]+"-"+end_date[-10:-8]+"-"+end_date[-8:-6]+" "\
                   +end_date[-6:-4]+":"+end_date[-4:-2]+":"+end_date[-2:]


        # x데이터 호출
        sql_select_tables = "select * from input1 " \
                            "where UPLOAD_DATE between STR_TO_DATE('" + start_date + "', '%Y-%m-%d %H:%i:%s') " \
                            "and STR_TO_DATE('" + end_date + "', '%Y-%m-%d %H:%i:%s') " \
                            "order by UPLOAD_DATE asc"
        cur.execute(sql_select_tables)

        # output을 날짜와 단어로 분리
        for _data in cur.fetchall():
            data = _data[1:] #todo datetime.datetim()의 형태로 나옴. 변경 필요
            dataX.append(data)
        print("dataX 호출 완료하였습니다.")

        # x데이터에 맞는 날짜 호출
        sql_select_tables2 = "select CAST(upload_date as char) from input1 " \
                             "where UPLOAD_DATE between STR_TO_DATE('" + start_date + "', '%Y-%m-%d %H:%i:%s') " \
                             "and STR_TO_DATE('" + end_date + "', '%Y-%m-%d %H:%i:%s') " \
                             "order by UPLOAD_DATE asc"
        cur.execute(sql_select_tables2)
        for date in cur.fetchall():
            date_list.append(date[0])
        print("dataX.date 호출 완료하였습니다.")

        # 존재하는 x데이터의 시간에 맞는 Y값 호출
        for i in range(len(date_list)):
            date = str(date_list['date'][i])
            date = date[:-10]+"-"+date[-10:-8]+"-"+date[-8:-6]+" "+date[-6:-4]+":"+date[-4:-2]+":"+date[-2:]
            sql_select_tables3 = "select y_hat from stock_price " \
                                 "where pcode='"+company+"' " \
                                 "and st_date=STR_TO_DATE('"+date+"','%Y-%m-%d %H:%i:%s')"
            cur.execute(sql_select_tables3)
            for item in cur.fetchone():
                dataY.append(item)
        print("dataY 호출 완료하였습니다.")

        print(company+"의 "+start_date+"~"+end_date+"까지 데이터를 호출하였습니다.")
    except mysql.DatabaseError as e:
        print('getDate Error : ', e)


    return dataX, dataY


if __name__ == "__main__":
    company = "039490"
    start_date = "20171121000000"
    end_date = "20171122000000"
    dataX, dataY = getData(company, start_date, end_date)
    print(dataX[0])
    print(dataY[0])

