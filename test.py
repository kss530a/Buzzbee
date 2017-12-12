# # from PyQt5.QtCore import QTime
# # from PyQt5.QtWidgets import QApplication
# # import sys
# # import datetime
# # from Kiwoom.Kiwoom import *
# import os
# import random
#
# # pcode="039490"
# # tempMaxPrice = 999999
# # MaxPrice={}
# # MaxPrice['{}'.format(pcode)]=tempMaxPrice
# #
# # print(MaxPrice['{}'.format(pcode)])
# #
# #
# # currentTime = QTime.currentTime().toString("hhmm")
# # currentTime = "201711"+currentTime + "00"
# # now = datetime.datetime.now().strftime('%Y%m%d%H%M')
# # print(now)
# #
# # print(currentTime)
# # print()
# #
# # test= [('276990', 'KODEX 글로벌4차산업로보틱스(합성)', '+12110', '-9905', None), ('273130', 'KODEX 종합채권(AA-이상)액티브', None, None, None), ('276990', 'KODEX 글로벌4차산업로보틱스(합성)', '+12110', '-9905', None), ('276990', 'KODEX 글로벌4차산업로보틱스(합성)', '+12110', '-9905', None), ('273130', 'KODEX 종합채권(AA-이상)액티브', None, None, None), ('039490', '키움증권', None, None, None), ('039490', '키움증권', None, None, None), ('039490', '키움증권', None, None, None), ('276990', 'KODEX 글로벌4차산업로보틱스(합성)', '+12110', '-9905', None)]
# # len(test)
# #
# # interestCompany = []
# # for company in test:
# #     company = list(company)
# #     print(company)
# #     interestCompany.append(company)
# #
# # cnt = len(interestCompany)
# #
# # # 테이블에 출력
# # for i in range(cnt):
# #     for j in range(len(interestCompany[i])):
# #         print(interestCompany[i][j])
#
#
# # tes = []
# # tes.append([])
# # print(tes)
# # if not tes[0]:
# #     print("asd")
# #
#
# # app = QApplication(sys.argv)
# # kiwoom = Kiwoom()
# # kiwoom.comm_connect()
# # screenNo = "0101"
# # codes= "039490;035420"
# # fids="10"
# # kiwoom.setRealReg(screenNo, codes, fids, "0") #이벤트 루프 생성되어 무제한 발생, 프로그램 종료시 이벤트 루프 exit
# # print("setRealReg 완료")
# # kiwoom.checkRealTimePrice(codes, fids)
# # print("now : "+kiwoom.nowPrice+", tempMax :"+ kiwoom.tempMaxPrice)
# # kiwoom.setRealRemove(screenNo, codes)
# # kiwoom.saveRealTimePrice()
# '''
# 1. setRealReg by interest_company
#     1.1 change setRealReg by adding interest_company
# 2. checkRealTimePrice for every 10 sec
# 3. saveRealTimePrice for every 1 min
# 4. setRealRemove by removing interest_company
# '''
#
# def check(times, amount):
#     earning = 0
#     loss = 0
#     answer = []
#     for i in range(0, times):
#         answer.append(random.randint(1,4))
#
#     for i in range(0, times):
#         pick = random.randint(1,4)
#         if pick == answer[i]:
#             loss -=  amount*3
#         else:
#             earning += amount*3.94
#     totalEarning = earning + loss
#
#     print("수익 : " + str(earning))
#     print("손실 : " + str(loss))
#     print("합계 : " + str(totalEarning))
#
#
# '''
# 1. 1회에 1폴당 amount만큼 3폴을 배팅
#     1.1 이길경우 amount * 3.94 획득
#     1.2 질경우 amount * 3 손실
#         1.2.1 1폴을 amount*3 으로 올린다(질경우 반복)
#         1.2.2 1로 돌아간다
# '''
#
# def checkCascade(times, amount):
#     earning = 0
#     loss = 0
#     answer = []
#     for i in range(0, times):
#         answer.append(random.randint(1, 4))
#
#     i=0
#     while (i==times):
#         pick= random.randint(1,4)
#         if pick == answer[i] :
#             loss -= amount*3
#             i += 1
#             pick = random.randint(1,4)
#             if pick == answer[i]:
#                 loss -= amount * 3 * 3
#                 i += 1
#                 if pick == answer[i]:
#                     loss -= amount * 3 * 3 * 3
#                     i += 1
#                     if pick == answer[i]:
#                         loss -= amount * 3 * 3 * 3 * 3
#                         i += 1
#                         if pick == answer[i]:
#                             loss -= amount * 3 * 3 * 3 * 3 * 3
#                             i += 1
#                         else:
#                             earning += amount * 3 * 3 * 3 * 3 * 3.94
#                             i += 1
#                     else:
#                         earning += amount * 3 * 3 * 3 * 3.94
#                         i += 1
#                 else:
#                     earning += amount * 3 * 3 * 3.94
#                     i += 1
#             else:
#                 earning += amount * 3 * 3.94
#                 i += 1
#         else:
#             earning += amount * 3.94
#             i += 1
#
#     totalEarning = earning + loss
#
#     print("수익 : " + str(earning))
#     print("손실 : " + str(loss))
#     print("합계 : " + str(totalEarning))
#
#
# times = 100
# amount = 3000
# check(times, amount)
# checkCascade(times, amount)

list = []
list.append("035420")
for code in list:
    print(code)