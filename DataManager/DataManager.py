__author__ = 'Oskar'
#Interface for the database retriver, weather, and holiday scrpits
#recommended to be used continually, since downloading all the databases and weatherdata
#at one time will be very time consuming.
#when initiating weather it is recommended to fetch the whole span of days you want to use
#all databases and weather lists will eventually fill up which will result in better performance
import Weather
import Holidays
import DatabaseRetriever_ver06

from datetime import date
from datetime import timedelta as td
from multiprocessing import Pool


class DataManager():
    def __init__(self, start=None, finish=None):
        self.weather = Weather.Weather(start, finish)
        self.holiday = Holidays.Holiday()
        self.db = DatabaseRetriever_ver06.Db()

    def collectByConditions(self, device, conditions):
        data_list = self.db.collect("mysql315.loopia.se", "kthstud@a68445", "2013IIstud!#", "aktivahuset_com",
                                   "meterevents", device, True)
        start_date = data_list[0][:data_list[0].find(" ")].split("-")
        start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        last_date = data_list[-1][:data_list[-1].find(" ")].split("-")
        last_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2]))

        weather_list = self.weather.fetchGroup(start_date, last_date)

        date_list = list()

        for condition in conditions:
            for day in weather_list:
                if condition in day.cond:
                    date.append(day)

        data_list = filter(lambda data: data[:data.find(" ")] in date_list, data_list)
        return data_list

    def collectByTemp(self, device, temp):
        data_list = self.db.collect("mysql315.loopia.se", "kthstud@a68445", "2013IIstud!#", "aktivahuset_com",
                                         "meterevents", device, True)
        start_date = data_list[0][:data_list[0].find(" ")].split("-")
        start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        last_date = data_list[-1][:data_list[-1].find(" ")].split("-")
        last_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2]))

        print "Fetching weather data.."
        weather_list = self.weather.fetchGroup(start_date, last_date)

        date_list = list()
        for day in weather_list:
            if temp[0] <= day.temp < temp[1]:
                date_list.append(day)

        print "Filtering.."
        data_list = filter(lambda data: data[:data.find(" ")] in date_list, data_list)

        return data_list

    def collectByHoliday(self, device):
        data_list = self.db.collect("mysql315.loopia.se", "kthstud@a68445", "2013IIstud!#", "aktivahuset_com",
                                         "meterevents", device, True)
        start_date = data_list[0][:data_list[0].find(" ")].split("-")
        start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        last_date = data_list[-1][:data_list[-1].find(" ")].split("-")
        last_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2]))
        delta = last_date - start_date
        date_list = list()

        for i in range(delta.days + 1):
            day = start_date + td(days=i)
            if self.holiday.check(day):
                date_list.append(day.__str__())

        print "Filtering.."
        data_list = filter(lambda data: data[:data.find(" ")] in date_list, data_list)

        return data_list

    def collectByWorkdays(self, device):
        data_list = self.db.collect("mysql315.loopia.se", "kthstud@a68445", "2013IIstud!#", "aktivahuset_com",
                                         "meterevents", device, True)
        start_date = data_list[0][:data_list[0].find(" ")].split("-")
        start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        last_date = data_list[-1][:data_list[-1].find(" ")].split("-")
        last_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2]))
        delta = last_date - start_date
        date_list = list()

        for i in range(delta.days + 1):
            day = start_date + td(days=i)
            if not self.holiday.check(day):
                date_list.append(day.__str__())

        print "Filtering.."
        data_list = filter(lambda data: data[:data.find(" ")] in date_list, data_list)

        return data_list

    def collectByWeekday(self, device, weekday):
        data_list = self.db.collect("mysql315.loopia.se", "kthstud@a68445", "2013IIstud!#", "aktivahuset_com",
                                         "meterevents", device, True)
        start_date = data_list[0][:data_list[0].find(" ")].split("-")
        start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        last_date = data_list[-1][:data_list[-1].find(" ")].split("-")
        last_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2]))
        delta = last_date - start_date

        date_list = list()
        for i in range(delta.days + 1):
            day = start_date + td(days=i)
            if day.weekday() == weekday:
                date_list.append(day.__str__())

        print "Filtering.."
        data_list = filter(lambda data: data[:data.find(" ")] in date_list, data_list)

        return data_list

    def BETAcollectByWeekday(self, device, weekday):
        data_list = self.db.collect("mysql315.loopia.se", "kthstud@a68445", "2013IIstud!#", "aktivahuset_com",
                                    "meterevents", device, True)
        start_date = data_list[0][:data_list[0].find(" ")].split("-")
        start_date = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        last_date = data_list[-1][:data_list[-1].find(" ")].split("-")
        last_date = date(int(last_date[0]), int(last_date[1]), int(last_date[2]))
        delta = last_date - start_date

        date_list = list()
        for i in range(delta.days + 1):
            day = start_date + td(days=i)
            if day.weekday() == weekday:
                date_list.append(day.__str__())

        def thread(data):
            new_list=list()
            for x in data:
                if x[:x.find(" ")] in date_list:
                    new_list.append(x)
            return new_list

        print "Filtering.."
        data_list = zip(*[iter(data_list)] * 4)
        p = Pool(4)
        result = p.apply_async(thread, data_list)
        #data_list = filter(lambda data: data[:data.find(" ")] in date_list, data_list)
        #data_list = p.map(thread, data_list)
        return result

if __name__ == '__main__':

    dm = DataManager()
    #hej = dm.collectByWorkdays("Office")
    hej = dm.collectByWeekday("Office", 3)
    print hej
