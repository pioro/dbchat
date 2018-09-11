import cx_Oracle


connection = cx_Oracle.connect(
    user="scott", password="tiger",
    dsn="172.16.180.129/test121")

print "====================================="
print "no bind"
print "====================================="


sqltext = """
select empno, ename from emp
"""

cursor = connection.cursor()
cursor.execute(sqltext)
for empno, ename in cursor:
    print empno, ename

print "====================================="
print "bind"
print "====================================="

sqltext = """
select empno, ename from emp
where empno > :empno
"""

bind = { "empno" : 7900 }

cursor = connection.cursor()
cursor.execute(sqltext, bind)

rowlist = cursor.fetchall()

for empno, ename in rowlist:
    print empno, ename
