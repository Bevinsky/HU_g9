import MySQLdb as mdb
##http://phpmyadmin315.loopia.se/
##
##anv:kthstud@a68445
##
##losen:2013IIstud!#
##
##(host='mysql315.loopia.se', user='username', passwd='some pwd', db='aktivahuset_com')

conn=mdb.connect("mysql315.loopia.se","kthstud@a68445","2013IIstud!#","aktivahuset_com")
with conn:
    cur=conn.cursor()
    cur.execute("SELECT * FROM *")
    rows=cur.fetchall()
    for rom in rows:
        print row
