import MySQLdb as mdb

conn=mdb.connect()
with conn:
    cur=conn.cursor()
    cur.execute("SELECT * FROM *")
    rows=cur.fetchall()
    for rom in rows:
        print row
