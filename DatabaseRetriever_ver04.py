##Hamtar all data sedan senaste hamtningen
##behover python 2.7 och MySQL-python installerat

import MySQLdb as mdb
from Tkinter import *
import pickle
from datetime import datetime
from time import strptime
import os
idDict=dict()
idDict["Plugwise.000D6F00003FE5A5"]="Livningroom"
idDict["Plugwise.000D6F000046957C"]="Dishwasher"
idDict["Plugwise.000D6F0000469D83"]="Office"
idDict["Plugwise.000D6F000055138F"]="Bedroom"
idDict["Plugwise.000D6F0000599D9B"]="Kettle"
idDict["Plugwise.000D6F000072A183"]="WashingMachine"
idDict["Plugwise.000D6F000397AA8A"]="MicrowaveOven"
idDict["Plugwise.000D6F00039745B7"]="KitchenFan"
idDict["Plugwise.000D6F000397AAFA"]="Dehumidifier"
idDict["Plugwise.000D6F00039745EF"]="Refridgerator"
idDict["Plugwise.000D6F00039747EC"]="Toaster"
idDict["Plugwise.000D6F0001A40370"]="Mains1"
idDict["Plugwise.000D6F0001A40664"]="Mains2"
idDict["Plugwise.000D6F0000D31BBE"]="Mains3"
idDict["Plugwise.Total"]="TotalEnergy"

invIdDict = {v:k for k, v in idDict.items()}

class DatabaseRetriever:
    def __init__(self):
        self.root=Tk()
        self.frame=Frame(self.root)
        self.frame.master.title("Database Retreiver")
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        self.frame.master.geometry('%dx%d+%d+%d' % (220, 210, (ws/2) - (220/2), (hs/2) - (210/2)))
        self.create_widgets()
        self.root.mainloop()
        
    def create_widgets(self):
        self.frame.pack(padx=5,pady=5)
        hostLabel = Label(self.frame)
        hostLabel.grid(row=1,column=0,pady=3,sticky=W)
        hostLabel["text"] = "Host:"

        hostEntry = Entry(self.frame)
        hostEntry.grid(row=1,column=1,pady=3)
        hostEntry["width"] = 20

        userLabel = Label(self.frame)
        userLabel.grid(row=2,column=0,sticky=W,pady=3)
        userLabel["text"] = "User:"
        
        userEntry = Entry(self.frame)
        userEntry.grid(row=2,column=1,pady=3)
        userEntry["width"] = 20
        
        passLabel = Label(self.frame)
        passLabel["text"] = "Password:"
        passLabel.grid(row=3,column=0,sticky=W,pady=3)

        passEntry = Entry(self.frame)
        passEntry["width"] = 20
        passEntry.grid(row=3,column=1)

        dbLabel = Label(self.frame)
        dbLabel["text"] = "Database:"
        dbLabel.grid(row=4,column=0,sticky=W,pady=3)

        dbEntry = Entry(self.frame)
        dbEntry["width"] = 20
        dbEntry.grid(row=4,column=1)

        tableLabel = Label(self.frame)
        tableLabel["text"] = "Table:"
        tableLabel.grid(row=5,column=0,sticky=W,pady=3)

        tableEntry = Entry(self.frame)
        tableEntry["width"] = 20
        tableEntry.grid(row=5,column=1)

        deviceLabel = Label(self.frame)
        deviceLabel["text"] = "Device:"
        deviceLabel.grid(row=6,column=0,sticky=W,pady=3)

        var = StringVar()
        var.set(invIdDict.keys()[0])
        #OptionMenu(self.frame, var, tuple(invIdDict.keys())).grid(row=6,column=1)
        apply(OptionMenu, (self.frame, var) + tuple(invIdDict.keys())).grid(row=6,column=1)
        
        Button(self.frame,text='Get database',command=(lambda: self.connect_to(hostEntry.get(),userEntry.get(),passEntry.get(),dbEntry.get(),tableEntry.get(),var.get()))).grid(row=7,column=0,padx=1,columnspan=2)
        self.enter=lambda event: self.connect_to(hostEntry.get(),userEntry.get(),passEntry.get(),dbEntry.get(),tableEntry.get(),var.get())
        tableEntry.bind('<Return>',self.enter)

    def connect_to(self,host,user,password,db,table,device):
        self.root.destroy()
        lastTimeTag="0000-00-00 00:00:00"
        dataCollection=list()
        file_not_found=0
        try:
            old=open(str(device)+".csv","rb")

            print "Previous data found, will merge with new"
            lines=old.readlines()
            old.close()
            newfile=open(str(device)+".csv","wb")
            for line in lines:
                newfile.write(line)
                
            #ast.litheral.eval()
            tempList=eval(lines[-1])
            print tempList
            lastTimeTag=tempList[0].strftime("%Y-%m-%d %H:%M:%S")
            print lastTimeTag
        except IOError:
            file_not_found=1
            print "No previous data, complete database will be retrieved.."

        if file_not_found:
            newfile=open(str(table)+".csv","wb")
            
        print "Connecting to database with Host:"+str(host)+" User:"+str(user)+" Password:"+str(password)+" DB:"+str(db)+" Table:"+str(table)+" Device:"+str(device)
        
        try:
            conn= mdb.connect(host=str(host),user=str(user),passwd=str(password),db=str(db))
            #conn = mdb.connect(host='mysql315.loopia.se', user='kthstud@a68445', passwd='2013IIstud!#', db='aktivahuset_com')
            
        except Exception as e:
            print e
            return
        print "Connected.."
        with conn:
            cur=conn.cursor()
            #sql="SELECT * FROM {0} WHERE id='{1}' OR id='{2}'".format(table,str(invIdDict[device]),str(idDict[invIdDict[device]]))
            sql="SELECT * FROM {0} WHERE time>'{1}'".format(table,lastTimeTag)
            print "Using: "+sql
            cur.execute(sql)
            rows=cur.fetchall()
            for row in rows:
                #print row[0]
                newfile.write(str(row[0])+";"+str(row[3])+"\n")
                #print row
            newfile.close()
            return
        newfile.close()
        os.remove(str(table)+".csv")
        return
            
if __name__=='__main__':
    DatabaseRetriever()
    print "Done"
