from Kiwoom.Kiwoom2 import *
import cx_Oracle as mysql
from PyQt5.QtCore import Qt, QTimer, QTime, QEventLoop


"""
:param pcodes: string - 종목코드 리스트(종목코드;종목코드;...)
:param fids: string - fid 리스트(fid;fid;...)
:return
"""
def realTimePrice(pcodes, fids):
    kiwoom = Kiwoom()
    kiwoom.commConnect()
    temp = []
    pcode_list = pcodes.split(';')

    loginLoop = QEventLoop()
    loginLoop.exec_()

    # 매분의 0, 10, 20, 30, 40, 50초 시점마다 실행하여 실시간데이터를 가져와서
    kiwoom.setRealReg("0101", pcodes, fids, "0")
    print(pcodes + "의 주식시세")
    print(kiwoom.testdata)
    temp.append(kiwoom.testdata)

    # todo 종목별 가격 저장
    for pcode in pcode_list:
        return pcode

    # todo 종목별 최고가 탐색
    maxPrice = 0
    for price in temp:
        if price > max:
            maxPrice = price

    # 최고가를 해당 분의 가격으로 DB에 저장한다.
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()
        nowDate = 0 #todo 저장할 시간 탐색
        # "insert into stock_price values(to_date('2017-11-27 14:15:00', 'yyyy-mm-dd hh24:mi:ss'), 'company', 87000)"
        sql_insert_tables = "insert into stock_price(st_date, pcode, price) " \
                            "values(to_date('"+nowDate+" 'yyyy-mm-dd hh24:mi:ss'), " \
                            "'종목코드', maxPrice)" #todo sql문 완성
        cur.execute(sql_insert_tables)
        conn.commit()

        print()

    except mysql.DatabaseError as e:
        print('Error : ', e)

    finally:
        cur.close()
        conn.close()


# setRealReg(self, screenNo, codes, fids, realRegType)
# :param screenNo: string
# :param codes: string - 종목코드 리스트(종목코드;종목코드;...)
# :param fids: string - fid 리스트(fid;fid;...)
# :param realRegType: string - 실시간등록타입(0: 첫 등록, 1: 추가 등록)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pcodes = "039490;035420"
    fids = "10"
    realTimePrice(pcodes, fids)
