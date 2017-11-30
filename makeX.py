'''
1. DBMS에서 input tables를 join하고 word 속성만 추출
or
1. csv파일로 받아서 여러 csv 합치기
'''
import cx_Oracle as mysql
import hyperParameters as hp
import numpy as np
import csv
import os


# hyper-parameters # 미완
data_dim = hp.getHyparam("data_dim") #단어 수
non_word_num = hp.getHyparam("non_word_num")

def makeX(type):

    # DBMS 활용
    if type=="mysql":
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()
        x_data = []

        #특정속성(id, date 등) 제외하고 워드 속성만 가져오기
        sql_select_tables = "select * " \
                            "from input0 i0, input1 i1, input2 i2" \
                            "where input0.oid=input1.oid and input1.oid=input2.oid"

        cur.execute(sql_select_tables)
        record_list = cur.fetchall()


        #words 속성들로 행렬만들기
        for i in range(0, len(record_list)/data_dim):
            _x = record_list[i*data_dim : (i+1)*data_dim]
            x_data.append(_x)


    elif type=="csv":
        # csv 활용, 여러 csv 합치기
        csv_dir = r'/csv'
        merged_dir = r'/mergedcsv'
        merged_name = merged_dir + 'merged.csv'
        merged_file = open(merged_name, 'W', newline='', encoding='utf-8')

        csv_list = os.listdir(csv_dir)
        csv_writer = csv.writer(merged_file)

        for csv_name in csv_list:
            current_csv = csv_dir + csv_name
            current_file = open(current_csv, 'r', encoding='utf-8')
            csv_reader = csv.reader(current_file)



        x_ = np.loadtxt('input_sample.csv', delimiter=',')
        x_data = x_[:, non_word_num:-1]


    return x_data


print(makeX("csv"))
