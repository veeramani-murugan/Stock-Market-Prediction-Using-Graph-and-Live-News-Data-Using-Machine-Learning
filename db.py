import sqlite3
con = sqlite3.connect('signup.db')
#con.execute("alter table info add role varchar(50)")

con.commit()
e=con.execute("select * from info").fetchall()
print(e)
con.close()
