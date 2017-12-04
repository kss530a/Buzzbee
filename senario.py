from PyQt5 import uic
from Kiwoom.Kiwoom import *
from getX import *
import savePrice
from transaction import *
from interest_company import *

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

app = QApplication(sys.argv)
company = "039490"
start_date ="20171120000000"
end_date = "20171125000000"

makeY.makeY(company)
#dataX=getX(start_date, end_date)
#print(dataX)
