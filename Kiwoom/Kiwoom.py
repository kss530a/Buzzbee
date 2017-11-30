import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time
import csv

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    #키움API 인스턴스 생성
    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    #신호를 받기 위한 슬롯
    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        #self.OnReceiveChejanData.connect(self._receive_chejan_data())

    #접속 요청 with 이벤트루프
    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec()

    #접속 요청에 따른 결과 리턴
    def _event_connect(self, err_code):
        if err_code == 0:
            print("Connected")
        else:
            print("Disconnected")
        self.login_event_loop.exit()

    #시장별 코드리스트 호출
    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    #코드에 맞는 종목명 호출
    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    #연결상태 확인
    def get_connect_state(self):
        ret = self.dynamicCall("GetConnectState()")
        return ret

    #API에 입력정보 셋팅
    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    #API에 데이터 요청
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop() #반환값 올때까지 대기
        self.tr_event_loop.exec()

    #받아온 데이터에서 특정값 가져오기
    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)",
                               code, real_type, field_name, index, item_name)
        return ret.strip() # 반환값에 공백 제거하기 위하여 strip() 사용

    #받아온 데이터 수 확인
    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    #TR 요청 결과 이벤트 처리
    #1TR => 900 return 제한 => 요청데이터가 900개가 넘는경우 추가요청 필요
    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        #연속데이터 존재시 netx=2 반환 => 추가 TR
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)
        elif rqname == "opw00001_req":
            self._opw00001(rqname, trcode)
        elif rqname == "opt10080_req":
            self._opt10080(rqname, trcode)
        elif rqname == "opw00018_req":
            self._opw00018(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    #예수금d+2 조회
    def _opw00001(self, rqname, trcode):
        d2_deposit = self._comm_get_data(trcode, "", rqname, 0, "d+2추정예수금")
        self.d2_deposit = Kiwoom.change_format(d2_deposit)


    #분봉차트조회요청
    def _opt10080(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "체결시간")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")

            if (high[0] == "-"):
                high = high[1:]
            elif high[0] =="+":
                high = high[1:]

            self.data['date'].append(date)
            self.data['high'].append(high)




    #일봉차트조회요청
    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")
            print(date, open, high, low, close, volume)

    #opw00018 반환값을 위한 리스트 생성
    def reset_opw00018_output(self):
        self.opw00018_output = {'single': [], 'multi': []}

    #계좌평가잔고내역 요청
    def _opw00018(self, rqname, trcode):
        # single data
        total_purchase_price = self._comm_get_data(trcode, "", rqname, 0, "총매입금액")
        total_eval_price = self._comm_get_data(trcode, "", rqname, 0, "총평가금액")
        total_eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, 0, "총평가손익금액")
        total_earning_rate = self._comm_get_data(trcode, "", rqname, 0, "총수익률(%)")
        estimated_deposit = self._comm_get_data(trcode, "", rqname, 0, "추정예탁자산")

        self.opw00018_output['single'].append(Kiwoom.change_format(total_purchase_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_profit_loss_price))

        total_earning_rate = Kiwoom.change_format(total_earning_rate)

        if self.get_server_gubun():
            total_earning_rate = float(total_earning_rate) / 100
            total_earning_rate = str(total_earning_rate)

        self.opw00018_output['single'].append(total_earning_rate)
        self.opw00018_output['single'].append(Kiwoom.change_format(estimated_deposit))

        # multi data
        rows = self._get_repeat_cnt(trcode, rqname)
        for i in range(rows):
            name = self._comm_get_data(trcode, "", rqname, i, "종목명")
            quantity = self._comm_get_data(trcode, "", rqname, i, "보유수량")
            purchase_price = self._comm_get_data(trcode, "", rqname, i, "매입가")
            current_price = self._comm_get_data(trcode, "", rqname, i, "현재가")
            eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, i, "평가손익")
            earning_rate = self._comm_get_data(trcode, "", rqname, i, "수익률(%)")

            quantity = Kiwoom.change_format(quantity)
            purchase_price = Kiwoom.change_format(purchase_price)
            current_price = Kiwoom.change_format(current_price)
            eval_profit_loss_price = Kiwoom.change_format(eval_profit_loss_price)
            earning_rate = Kiwoom.change_format2(earning_rate)

            self.opw00018_output['multi'].append([name, quantity, purchase_price, current_price, eval_profit_loss_price,
                                                  earning_rate])




    #주문체결 요청
    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString",
                         [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])

    #주문체결 후 잔고 요청
    def get_chejan_data(self, fid):
        ret = self.dynamicCall("GetChejanData(int)", fid)
        return ret

    #추문 체결시 키움이벤트 처리
    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(gubun)
        print(self.get_chejan_data(9203))
        print(self.get_chejan_data(302))
        print(self.get_chejan_data(900))
        print(self.get_chejan_data(911))

    #사용자 정보 및 계좌정보 요청
    def get_login_info(self, tag):
        ret = self.dynamicCall("GetLoginInfo(QString", tag)
        return ret

    #Static-method, 좌측 0,- 제거 및 콤마(,) 추가
    def change_format(data):
        strip_data = data.lstrip('-0')
        if strip_data == '' or strip_data == '.00':
            strip_data = '0'

        format_data = format(int(strip_data), ',d')
        if data.startswith('-'):
            format_data = '-' + format_data

        return format_data

    #수익률에 대한 포맷 변경, 실서버와 모의서버 구별해야함
    def change_foramt2(data):
        strip_data = data.lstrip('-0')

        if strip_data =='':
            strip_data ='0'

        if strip_data.startswith('.'):
            strip_data = '0' + strip_data

        if data.startswith('-'):
            strip_data = '-' + strip_data

        return strip_data

    #모의투자 서버와 실투자서버 구분
    def get_server_gubun(self):
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()
    kiwoom.data = {'date': [], 'high': []}

    '''#일봉주가 요청(opt10081)
    kiwoom.set_input_value("종목코드", "039490")
    kiwoom.set_input_value("기준일자", "20170224")
    kiwoom.set_input_value("수정주가구분", 1)
    kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    while kiwoom.remained_data == True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.set_input_value("종목코드", "039490")
        kiwoom.set_input_value("기준일자", "20170224")
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")'''
    '''
    # 분봉주가 요청(opt10080)
    time.sleep(TR_REQ_TIME_INTERVAL)
    kiwoom.set_input_value("종목코드", "039490")
    kiwoom.set_input_value("틱범위", "1:1분")
    kiwoom.set_input_value("수정주가구분", 1)
    kiwoom.comm_rq_data("opt10080_req", "opt10080", 0, "0101")

    while kiwoom.remained_data == True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.set_input_value("종목코드", "039490")
        kiwoom.set_input_value("틱범위", "1:1분")
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10080_req", "opt10080", 2, "0101")

        csv_file = open('stock_price_kiwoom.csv', 'w', encoding='UTF-8')
        csv_writer = csv.writer(csv_file, delimiter=',')
        for i in range(0, len(kiwoom.data['date'])):
            csv_writer.writerow((kiwoom.data['date'][i], kiwoom.data['high'][i]))
        csv_file.close()
    '''

    '''
    #매매 요청
    acc_no = "8098264611"#kiwoom.get_login_info("ACCNO") ##계좌정보
    order_type = 0 ##신규매수:1,신규매도:2,매수취소:3,매도취소:4
    code = "039490" ##종목코드
    quantity = "1" ##매매수량
    price = "0" #지정가
    hoga = "03" #지정가:00, 시장가:03
    # 매매 요청
    kiwoom.send_order("send_order_req", "0101", acc_no, order_type, code, quantity,
                      price, hoga, "")
    '''

