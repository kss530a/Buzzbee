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
import cx_Oracle as mysql
import datetime

#hyper-parameters
limitTimePoint=float(hp.getHyparam("limitTimePoint")) #상승시점 분포 기준
decideY=float(hp.getHyparam("decideY")) #기사 발행시점 이후 limitTime 이내 판매가 이상 유지시간

#savePrice()에 의해 DB에 저장된 [date, price]정보를 가져와 반환
#ex. price= getPrice("039490", "20171025125500", "20171025133600")
def getPrice(company, start_date, end_date):
    price=[]
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        sql_select_tables = "select price " \
                            "from stock_price " \
                            "where pcode='" + company + "' "\
                            "and st_date between to_date('"+start_date+"', 'YYYYMMDDHH24MISS') " + \
                            "and to_date('"+end_date+"', 'YYYYMMDDHH24MISS') " \
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


def getLimitTime(company):
    stnd_price= []
    eachAscTimes = []

    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        '''매번 DB에 접근하여 느림
        #기사들의 date 가져오기
        sql_select_tables = "select to_char(st_date, 'YYYYMMDDHH24MISS') " \
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


def makeY(company):
    stnd_price=[]
    date_list = []
    y_list = []
    y_hat = 99
    executemany = []

    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        #날짜정보 가져오기
        sql_select_tables = "select to_char(st_date, 'YYYYMMDDHH24MISS') " \
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
        print(np.mean(y_list))

        #날짜에 맞는 y_hat 값 넣기
        for i in range(0, len(date_list)-60):
            _date = str(date_list[i])
            _y_hat = str(y_list[i])
            sql_update_tables = "update stock_price " \
                                "set y_hat=" + _y_hat + " " \
                                "where st_date=to_date('"+_date+"','YYYYMMDDHH24MISS')"
            cur.execute(sql_update_tables)
        conn.commit()

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

def getY(company, start_date, end_date):
    dataY = []
    return dataY

if __name__ == "__main__":
    makeY("550041")
    #price= getPrice("039490", "20171025125500", "20171025133600")
    #print(price)
