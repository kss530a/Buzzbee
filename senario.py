from PyQt5 import uic
from PyQt5.QtCore import QTimer

from Kiwoom.Kiwoom2 import *
from make_sub_tables import *
from tfData import *

'''
-------------------------------------------------------------------
1. 특정 회사 지정 by register_interest_company(pcode)
2. 과거 데이터 수집
    2.1 특정 회사의 주가 데이터 at Kiwoom by savePrice(company)
    2.2 기사 데이터 at naver by clawler
3. 과거 데이터 전처리
    3.1 수집된 주가 데이터를 활용하여 Y_hat 만들기 by makeY(company)
    3.2 기사 데이터 NLP, Clustering
4. 데이터를 활용하여 모델 학습시키기 by trainning_bee(dataX, dataY)
-------------------------------------------------------------------
5. 실시간 데이터 수집
    5.1 주가 데이터 at Kiwoom by (미완성)
    5.2 기사 데이터 at naver by clawler
6. 학습된 모델과 실시간 데이터 활용 (미완성)
    - Input data : 최근 1분간 기사 데이터의 집합
    - output data : Y_hat
7. Y_hat에 따른 Transaction (미완성)
-------------------------------------------------------------------
+@ 모델 튜닝
+@ UI 만들기
'''

if __name__ == "__main__":
    print("---------Scenario.1 시작---------")
    # app = QApplication(sys.argv)
    # kiwoom = Kiwoom()
    # kiwoom.commConnect()
    # print("키움API 접속 완료")

    # 기본 테이블 생성
    # create_company_info_table()
    # creat_stock_price_table()
    # create_interest_company_table()
    # print("기본테이블 생성 완료")

    # 기본 회사정보 입력
    # kiwoom.insertCompanyInfoTable()
    # print("회사정보 호출 및 저장 완료")

    # 테스트 할 회사명과 날짜
    # company = "039490"
    # Y_start_date ="20171127000000"
    # Y_end_date = "20171201000000"
    # X_start_date ="20171121000000"
    # X_end_date = "20171122000000"

    # 주식정보 저장하기
    code_list =["590010", "035420", "035720", "036570", "039130", "039570", "010950", "009290", "004170", "039490"]
    # update interest_company set eval_index=0.844 where pcode='590010';
    # update interest_company set eval_index=0.123 where pcode='035420';
    # update interest_company set eval_index=0.177 where pcode='035720';
    # update interest_company set eval_index=0.243 where pcode='036570';
    # update interest_company set eval_index=0.167 where pcode='039130';
    # update interest_company set eval_index=0.268 where pcode='039570';
    # update interest_company set eval_index=0.120 where pcode='010950';
    # update interest_company set eval_index=0.109 where pcode='009290';
    # update interest_company set eval_index=0.208 where pcode='004170';
    # update interest_company set eval_index=0.159 where pcode='039490';

    for code in code_list:
        makeY(code)
        print(code+"의 Y값 구하기 완료 ")
        print("------------------------")



    #
    # makeY(company)
    # print("Y데이터 생성 완료")
    #
    # dataY=getY(company, Y_start_date, Y_end_date)
    # print("dataY 호출 완료.")
    # print("첫번째 Y 값 : "+str(dataY[0]))
    # dataX=getX(str(X_start_date), str(X_end_date))
    # print("키움API 접속 완료")
    # print("첫번째 X 값 : "+str(dataX[0]))
    print("---------Scenario1 종료---------")

