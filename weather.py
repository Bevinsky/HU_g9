import wap
from datetime import date
from datetime import timedelta as td
import pickle

months=["January","February","March","April","May","June","July","August","September","October","November","December"]
    
dayWeatherList=list()

__APPID__="X8JJ7X-8R4Q7GJJ42"

class DayWeather():
    def __init__(self,date='',temp='',conditions='',humidity='',wind=''):
        self.date=date
        self.temp=temp
        self.conditions=conditions
        self.humidity=humidity
        self.wind=wind
        
def collect(startTime=date(2012,10,11),stopTime=date(2013,02,12)):
    delta=stopTime-startTime
    dateList=list()
    for i in range(delta.days+1):
        day=startTime+td(days=i)
        dateList.append(day)
    client=wap.WolframAlphaEngine(__APPID__,'http://api.wolframalpha.com/v1/query.jsp')
    for day in dateList:
        inputQuery=str("weather in stockholm on "+months[day.month-1]+" "+str(day.day)+", "+str(day.year))
        print "Using query: "+inputQuery
        q=wap.WolframAlphaQuery(inputQuery,__APPID__)
        q.ScanTimeout = '3.0'
        q.Async = False
        q.ToURL()
         
        result = client.PerformQuery(q.Query)
        qresult = wap.WolframAlphaQueryResult(result)
        #print qresult
        pod=qresult.Pods()[1]
        #print pod
        np = wap.Pod(pod)
        subpods=np.Subpods()
        data=subpods[0][1][1]

        temp=data[data.find("temperature | ")+14:data.find("conditions | ")]
        conditions=data[data.find("conditions | ")+13:data.find("relative humidity | ")]
        humidity=data[data.find("relative humidity | ")+20:data.find("wind speed | ")]
        wind=data[data.find("wind speed | ")+13:]

        dayWeatherList.append(DayWeather(day.__str__(),temp,conditions,humidity,wind))

    try:
        newfile=open("Weatherdata2.pkl","wb")
        pickle.dump(dayWeatherList,newfile)
        newfile.close()
    except IOError:
        for x in dayWeatherList:
            print x.date
            print x.temp
            print x.conditions
            print x.humidity
            print x.wind

if __name__=="__main__":
    collect()
    
