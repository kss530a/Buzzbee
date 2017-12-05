import pymysql as mysql

#sub_tables
#company_info = {pcode(pk), pname}
#stock_price = {pcode(fk), st_date(pk), price}


# 회사 정보를 넣을 테이블 생성
def create_company_info_table():
    #테이블 생성
    try:
        conn = mysql.Connect(host='localhost',user='seungsu',password='tmdtn12',db='seungsu', charset='utf8')
        cur = conn.cursor()
        sql_create_tables = "create table company_info(" \
                            "pcode varchar(8) primary key," \
                            "pname varchar(40) not null, " \
                            "eval_index DECIMAL(1,3)" \
                            ")"
        cur.execute(sql_create_tables)
        print("company_info 테이블 생성 완료")
    except mysql.DatabaseError as e:
        print('creat_company_info_table Error : ', e)


# 주식가격을 저장할 테이블 생성
def creat_stock_price_table():
    try:
        conn = mysql.Connect(host='localhost',user='seungsu',password='tmdtn12',
                                        db='seungsu', charset='utf8mb4')
        cur = conn.cursor()

        sql_create_tables = "create table stock_price(" \
                            "st_date datetime not null," \
                            "pcode varchar(8) not null," \
                            "price mediumint not null," \
                            "y_hat tinyint," \
                            "CONSTRAINT stock_price_pk primary key (st_date, pcode), " \
                            "foreign key (pcode) references company_info(pcode)" \
                            ")"

        cur.execute(sql_create_tables)
        print("stock_price 테이블 생성 완료")
    except mysql.DatabaseError as e:
        print('Error : ', e)
    finally:
        cur.close()
        conn.close()

# 관심회사를 등록할 테이블 생성
def create_interest_company_table():
    try:
        conn = mysql.Connect(host='localhost',user='seungsu',password='tmdtn12',
                                        db='seungsu', charset='utf8mb4')
        cur = conn.cursor()

        sql_create_tables = "create table interest_company(" \
                            "pname varchar(40), " \
                            "pcode varchar(8), " \
                            "eval_index DECIMAL(1,3), " \
                            "high250 mediumint, " \
                            "low250 mediumint, " \
                            "primary key (pcode), "\
                            "foreign key (pcode) references company_info(pcode)" \
                            ")"
        print("interest_company 테이블 생성 완료")
        cur.execute(sql_create_tables)

    except mysql.DatabaseError as e:
        print('make_interest_company_table Error : ', e)
    finally:
        cur.close()
        conn.close()

# 테스트
if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # kiwoom = Kiwoom()
    # kiwoom.commConnect()
    # create_company_info_table()
    # insert_company_info_table()
    # creat_stock_price_table()
    create_interest_company_table()
    # pcode = "145210"
    # kiwoom.insert_interest_company_table(pcode)
    # kiwoom.update_interest_company(pcode)
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


