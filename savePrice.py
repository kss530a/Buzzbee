import cx_Oracle as mysql
from Kiwoom.Kiwoom2 import *
import time


# 분봉차트에서 가격데이터 저장

def savePrice(company):
    kiwoom = Kiwoom()
    kiwoom.commConnect()
    kiwoom.data = {'date': [], 'high': []}
    TR_REQ_TIME_INTERVAL=0.2
    # 분봉주가 요청(opt10080)
    time.sleep(TR_REQ_TIME_INTERVAL)
    kiwoom.setInputValue("종목코드", company)
    kiwoom.setInputValue("틱범위", "1:1분")
    kiwoom.setInputValue("수정주가구분", "1")
    kiwoom.commRqData("주식분봉차트조회요청", "opt10080", 0, "0101")

    while kiwoom.inquiry == '2':
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.setInputValue("종목코드", company)
        kiwoom.setInputValue("틱범위", "1:1분")
        kiwoom.setInputValue("수정주가구분", "1")
        kiwoom.commRqData("주식분봉차트조회요청", "opt10080", 2, "0101")

    # DB에 접속
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()
        print(kiwoom.data['date'])
        print(kiwoom.data['high'])
        # DB에 저장,  형태:20171127141500,-87000
        for i in range(len(kiwoom.data['date'])):
            year = kiwoom.data['date'][i][0:4]
            month = kiwoom.data['date'][i][4:6]
            day = kiwoom.data['date'][i][6:8]
            hour = kiwoom.data['date'][i][8:10]
            min = kiwoom.data['date'][i][10:12]
            # "insert into stock_price values(to_date('2017-11-27 14:15:00', 'yyyy-mm-dd hh24:mi:ss'), 'company', 87000)"
            sql_insert_tables = "insert into stock_price(st_date, pcode, price) " \
                                "values(to_date(\'" + str(year) + "-" + str(month) + "-" \
                                + str(day) + " " + str(hour) + ":" + str(min) + \
                                ":00\', \'yyyy-mm-dd hh24:mi:ss\'), " + "\'" + company + "\', " + \
                                kiwoom.data['high'][i] + ")"
            cur.execute(sql_insert_tables)
        conn.commit()

    except mysql.DatabaseError as e:
        print('Error : ', e)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.commConnect()
    kiwoom.savePrice("140910")
