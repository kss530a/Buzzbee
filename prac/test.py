
import cx_Oracle

con = cx_Oracle.connect("seungsu/tmdtn12")
cur = con.cursor()
cur.execute("select * from student")

for row in cur:
	print(row)
cur.close()
con.close()