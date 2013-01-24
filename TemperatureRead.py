import matplotlib.pyplot as plt


fileName="stockholm_timmedel.csv"
data=open(fileName,"r")
usefulData=list()
for line in data.readlines():
    x=line.split(";")
    if "2012" in x[0] or "2013" in x[0]:
        usefulData.append(x)
print usefulData
##axis=list()
##values=list()
##for event in x:
##    axis.append(x[1][:x[1].index(":")])
##    values.append(x[2].replace(",","."))
##
##print axis
##    
##plt.plot(values)
##plt.axis(axis)
##plt.show()
