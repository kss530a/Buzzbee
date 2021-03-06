import cx_Oracle as mysql
from Kiwoom.Kiwoom2 import *

#sub_tables
#company_info = {pcode(pk), pname}
#stock_price = {pcode(fk), st_date(pk), price}


def create_company_info_table():
    #테이블 생성
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()
        sql_create_tables = "create table company_info(" \
                            "pcode varchar(8) primary key," \
                            "pname varchar(40) not null, " \
                            "eval_index number(3)" \
                            ")"
        cur.execute(sql_create_tables)
        print("company_info 테이블 생성 완료")
    except mysql.DatabaseError as e:
        print('creat_company_info_table Error : ', e)
    finally:
        cur.close()
        conn.close()


#테이블 정보 넣기
def insert_company_info_table():
    kiwoom = Kiwoom()
    kiwoom.commConnect()

    #pcode 가져오기
    ret = kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
    kospi_code_list = ret.split(';')

    #pname 가져오기
    kospi_code_name_list = []
    for i in kospi_code_list:
        name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [i])
        kospi_code_name_list.append(name)

    #DB에 접속
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

    #db에 저장, 마지막 값 "" => 제거
        for i in range(len(kospi_code_list)-1):
            sql_insert_tables = "insert into company_info(pcode, pname) " \
                                "values('" + kospi_code_list[i] + "', '" \
                                + kospi_code_name_list[i] + "')"
            #확인용 print(sql_insert_tables)
            cur.execute(sql_insert_tables)
        print("company_info 테이블 정보 입력 완료")
        conn.commit()
    except mysql.DatabaseError as e:
        print('insert_company_info_table Error : ', e)
    finally:
        cur.close()
        conn.close()

def creat_stock_price_table():
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        sql_create_tables = "create table stock_price(" \
                            "st_date date not null," \
                            "pcode varchar(8) not null," \
                            "price number(10) not null," \
                            "y_hat number(1)," \
                            "foreign key (pcode) references company_info" \
                            ")"

        cur.execute(sql_create_tables)
        print("stock_price 테이블 생성 완료")
    except mysql.DatabaseError as e:
        print('Error : ', e)
    finally:
        cur.close()
        conn.close()

def create_interest_company_table():
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        sql_create_tables = "create table interest_company(" \
                            "pcode varchar(8) primary key, " \
                            "pname varchar(40), " \
                            "high250 number(10), " \
                            "low250 number(10), " \
                            "eval_index number(3), " \
                            "foreign key (pcode) references company_info" \
                            ")"
        print("interest_company 테이블 생성 완료")
        cur.execute(sql_create_tables)

    except mysql.DatabaseError as e:
        print('make_interest_company_table Error : ', e)
    finally:
        cur.close()
        conn.close()


#실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.commConnect()
    # create_company_info_table()
    # insert_company_info_table()
    # creat_stock_price_table()
    # create_interest_company_table()
    pcode = "145210"
    kiwoom.insert_interest_company_table(pcode)
    kiwoom.update_interest_company(pcode)
    '''
    #입력 확인
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()
        sql_select_tables = "select * from company_info"
        cur.execute(sql_select_tables)
        record_list = cur.fetchall()
        for pcode, pname in record_list:
            print(pcode, pname)
    except mysql.DatabaseError as e:
        print('Error : ', e)
    '''


