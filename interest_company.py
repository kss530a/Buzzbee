import cx_Oracle as mysql
import makeY
import savePrice
import hyperParameters


def register_interest_company(pcode):
    try:
        conn = mysql.connect("seungsu", "tmdtn12", "orcl")
        cur = conn.cursor()

        sql_select_tables = "select pname from company_info " \
                            "where pcode='"+ pcode +"'"
        cur.execute(sql_select_tables)
        pname = cur.fetchone()[0]

        sql_insert_tables = "insert into interest_company " \
                            "values('" + pcode + "', '"+ pname+"')"
        cur.execute(sql_insert_tables)
        conn.commit()

    except mysql.DatabaseError as e:
        print('makeY Error : ', e)
    finally:
        cur.close()
        conn.close()




if __name__ == "__main__":
    register_interest_company("039490")
