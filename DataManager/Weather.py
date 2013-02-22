# -*- coding:utf-8 -*-
"""
Will collect weather from wolframalpha. can do 7 day advance forecast
When initiating Weather class, you can choose to fetch the relevant days.
Once the data for a day is downloaded is will not need to be again even if program i closed.
always use collect for single day, not fetchday, since it will perform checks

"""
import wap
from datetime import date
from datetime import timedelta as td
import pickle

months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
    
dayWeatherList = list()

__APPID__ = "X8JJ7X-8R4Q7GJJ42"


class DayWeather():
    def __init__(self, date='', temp='', conditions='', humidity='', wind=''):
        self.date = date
        self.temp = temp
        self.conditions = conditions
        self.humidity = humidity
        self.wind = wind


class Weather():
    def __init__(self, start_time=None, last_time=None):
        self.day_list = list()
        try:
            newfile = open("Weatherdata.pkl", "rb")
            self.day_list = pickle.load(newfile)
            newfile.close()
        except IOError:
            raise
            #print "IOEroror"

        if start_time is not None and last_time is not None:
            try:
                self.fetchGroup(start_time, last_time)
            except IndexError:
                pass
            try:
                newfile = open("Weatherdata.pkl", "wb")
                pickle.dump(self.day_list, newfile)
                newfile.close()
            except IOError:
                pass
                #print "IOEroror"

    def collect(self, date):
        for day in self.day_list:
            if date.__str__() == day.date.__str__():
                return day
        if date <= date.today():
            new = self.fetchDay(date)
        elif (date - date.today()).days <= 7:
            new = self.fetchForecast(date)
        else:
            raise ValueError("Can't forecast more than 7 days in advance")
        self.day_list.append(new)

        try:
            newfile = open("Weatherdata.pkl", "wb")
            pickle.dump(self.day_list, newfile)
            newfile.close()
        except IOError:
            pass
            #print "IOEroror"

        return new

    def fetchDay(self, date):
        #print "fetchDay.."
        client = wap.WolframAlphaEngine(__APPID__, 'http://api.wolframalpha.com/v1/query.jsp')
        inputQuery = str("weather in stockholm on " + months[date.month - 1] + " " +
                         str(date.day) + ", " + str(date.year))
        print "Using query: " + inputQuery
        q = wap.WolframAlphaQuery(inputQuery, __APPID__)
        q.ScanTimeout = '3.0'
        q.Async = False
        q.ToURL()
        try:
            result = client.PerformQuery(q.Query)
            qresult = wap.WolframAlphaQueryResult(result)
            #print qresult
            pod = qresult.Pods()[1]
            #print pod
            np = wap.Pod(pod)
            subpods = np.Subpods()
            data = subpods[0][1][1]
            temp = data[data.find("temperature | ") + 14:data.find("conditions | ")]
            try:
                temp = int(temp[temp.find("average: ") + 9:temp.find(u" °C)")])
            except ValueError:
                temp = int(temp[:temp.find(u" °C")])
                #print "Temp:", temp
            # -40 - 40 interval with 5 per level
            conditions = data[data.find("conditions | ") + 13:data.find("relative humidity | ")]
            conditions = conditions[conditions.find("Cond: ") + 6:].split(" ")
            # some are to be regarded as same
            #print "Cond:", conditions
            humidity = data[data.find("relative humidity | ") + 20:data.find("wind speed | ")]
            #print "Humidity:", humidity
            wind = data[data.find("wind speed | ") + 13:]
            #print "Wind", wind

            return DayWeather(date, temp, conditions, humidity, wind)

        except IndexError:
            print "Index Error at PerformQuery, will try again.."
            return self.fetchDay(date)
        qresult = wap.WolframAlphaQueryResult(result)
        #print qresult
        pod = qresult.Pods()[1]
        #print pod
        np = wap.Pod(pod)
        subpods = np.Subpods()
        data = subpods[0][1][1]

        temp = data[data.find("temperature | ") + 14:data.find("conditions | ")]
        try:
            temp = int(temp[temp.find("average: ") + 9:temp.find(u" °C)")])
        except ValueError:
            temp = int(temp[:temp.find(u" °C")])
        #print "Temp:", temp
        # -40 - 40 interval with 5 per level
        conditions = data[data.find("conditions | ") + 13:data.find("relative humidity | ")]
        conditions = conditions[conditions.find("Cond: ") + 6:].split(" ")
        # some are to be regarded as same
        #print "Cond:", conditions
        humidity = data[data.find("relative humidity | ") + 20:data.find("wind speed | ")]
        #print "Humidity:", humidity
        wind = data[data.find("wind speed | ") + 13:]
        #print "Wind", wind

        return DayWeather(date, temp, conditions, humidity, wind)

    def fetchGroup(self, startTime, stopTime):
        if type(startTime) is not  date and type(stopTime) is not date:
            raise ValueError("Starttime and stoptime is not date-objects")

        delta = stopTime - startTime
        date_list = list()
        for i in range(delta.days + 1):
            day = startTime + td(days=i)
            date_list.append(day)

        new_days = list()

        for day in date_list:
            new = self.collect(day)
            new_days.append(new)

        return new_days

    def fetchForecast(self, date):
        print "fetchForecast.."
        client = wap.WolframAlphaEngine(__APPID__, 'http://api.wolframalpha.com/v1/query.jsp')
        inputQuery = str("weather in stockholm on " + months[date.month - 1] + " " +
                         str(date.day) + ", " + str(date.year))
        print "Using query: " + inputQuery
        q = wap.WolframAlphaQuery(inputQuery, __APPID__)
        q.ScanTimeout = '3.0'
        q.Async = False
        q.ToURL()
        try:
            result = client.PerformQuery(q.Query)
            qresult = wap.WolframAlphaQueryResult(result)
            #print qresult
            pod = qresult.Pods()[1]
            #print pod
            np = wap.Pod(pod)
            subpods = np.Subpods()
            data = subpods[0][1][1]
            if "no forecast available" in data:
                raise ValueError("No forecast available, even though less than 7 days")
            try:
                temp = int(data[:data.find(u" °C")])
            except ValueError:
                temp = int(data[data.find("between ") + 8:data.find(u" °C")])

            conditions = data[data.find(u" °C") + 3:].split("  |  ")
            return DayWeather(date, temp, conditions, None, None)
        except IndexError:
            print "Index Error at PerformQuery, will try again.."
            return self.fetchForecast(date)

if __name__ == "__main__":
    w = Weather()
    c = w.collect(date(2013, 02, 24))
    print c
