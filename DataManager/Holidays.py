from datetime import date
from datetime import timedelta as td
import pickle


class Holiday():
    def __init__(self):
        try:
            datafile = open("datum.pkl", "rb")
            self.holidayList = pickle.load(datafile)
            datafile.close()
        except IOError:
            raise IOError("No datumfile.pkl file, run blah.py first")

    def check(self, day):
        if not type(day) is date:
            try:
                day = date(day)
            except ValueError:
                return False
        if day.weekday() == 5 or day.weekday() == 6 or day in self.holidayList:
            return True
        
if __name__ == "__main__":
    h = Holiday()
    print h.check(date(2043, 06, 05))
