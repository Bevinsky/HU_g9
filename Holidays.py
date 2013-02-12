from datetime import date
from datetime import timedelta as td
import pickle
try:
    datefile=open("datum.pkl","rb")
except IOError:
    print "no datefile, run blah.py first"
    
holidayList=pickle.load(datefile)
datafile.close()

def holiday(day):
    if not type(day) is date:
        try:
            day=date(day)
        except ValueError:
            print "Not a date"
            return False
    print day.weekday()
    if day.weekday()==5 or day.weekday()==6 or day in holidayList:
        return True
        
if __name__=="__main__":
    print holiday(date(2043,06,05))
