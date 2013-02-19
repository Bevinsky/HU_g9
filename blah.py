"DTSTART;VALUE=DATE;ENCODING=8BIT;CHARSET=ISO-8859-1:"
"DURATION:P1D"
from datetime import *
import pickle
dates=list()
try:
    fil=open("Svenska helgdagar.ics","rb")
except IOError:
    print "no file to read from, download http://victor.se/bjorn/holidays.php?lang=en&year=&from=2011&to=2050"
for line in fil.readlines():
    
    if "DTSTART;VALUE=DATE;ENCODING=8BIT;CHARSET=ISO-8859-1:" in line:
        line=line.replace("\n","")
        data=line[line.find("DTSTART;VALUE=DATE;ENCODING=8BIT;CHARSET=ISO-8859-1:")+52:-1]
        data=data[:4] + "," + data[4:]
        data=data[:7] + "," + data[7:]
        data=datetime.strptime(data,"%Y,%m,%d").date()
        dates.append(data)
newfile=open("datum.pkl","wb")
pickle.dump(dates,newfile)
newfile.close()
