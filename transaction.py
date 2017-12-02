from Kiwoom.Kiwoom import *


order_type_lookup = {'신규매수':1, '신규매도':2, '매수취소':3, '매도취소':4}
hoga_lookup = {'지정가': "00", '시장가': "03"}

# 주식 구매, buy_stock("039490", 1, 12900, 10)
def buy_stock(company, y_hat, price, num):
    if (y_hat == 1) :

        account_number = kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        kiwoom.send_order("send_order_req", "0101",
                          account_number, "1", company, num, price, "00", "")

# 주식 판매, buy_stock("039490", 1, 13400, 10)
def sell_stock(company, price, num):
    account_number = kiwoom.get_login_info("ACCNO")
    account_number = account_number.split(';')[0]

    kiwoom.send_order("send_order_req", "0101",
                      account_number, "2", company, num, price, "00", "")
