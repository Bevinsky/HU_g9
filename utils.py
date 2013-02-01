import matplotlib.pyplot as plt
import numpy
import itertools
from collections import namedtuple as NT
import datetime


def intensity(total):
	total = sorted(total, key=lambda x: x.time)
	grp = plot_grouped(total, lambda x: x.time.weekday())
	alpha = 1.0/len(grp)
	min_ = 0
	for k in grp:
		min_ = min(min(grp[k]), min_)
	for k in grp:
		minutes = collect_total(grp[k], None)
		y = []
		for i in minutes:
			y.append(minutes[i])
		plt.fill_between(minutes.keys(), y, lw=0, alpha=alpha)
	plt.show()
	
	

def plot_grouped(data, xkey=lambda x: x, ykey=lambda y: y):
	sort = sorted(data, key=xkey)
	group = itertools.groupby(sort, xkey)
	grouped = {}
	for k, g in group:
		grouped[k] = map(ykey, list(g))
	
	x = grouped.keys()
	y = []
	for k in grouped.keys():
		y.append(grouped[k])
	
	return grouped
	#plt.xlabel(xlab)
	#plt.ylabel(ylab)
	#plt.bar(x, y)
	#plt.show()

def collect_total(total, key):
	sort = sorted(total, key=lambda t:t.time)
	first_day = sort[0]
	last_day = sort[-1]
	days_total = (last_day.time-first_day.time).days
	weighted = []
	nt = NT('energytuple', ['time', 'energy'])
	
	minutes = {}
	
	last = None
	for cur in sort:
		if last:
			last_minute = last.time.minute + last.time.hour*60
			cur_minute = cur.time.minute + cur.time.hour*60
			diff = cur.time-last.time
			if last_minute != cur_minute:
				remain = 60 - last.time.second
				if last_minute not in minutes:
					minutes[last_minute] = 0.0
				minutes[last_minute] += remain*last.rate
				diff -= datetime.timedelta(0, remain)
				while diff.seconds >= 60:
					last_minute += 1
					if last_minute >= 1440:
						last_minute = 0
					if last_minute not in minutes:
						minutes[last_minute] = 0.0
					minutes[last_minute] += 60*last.rate
					diff -= datetime.timedelta(0, 60)
				last_minute += 1
				if last_minute >= 1440:
					last_minute = 0
				if last_minute not in minutes:
					minutes[last_minute] = 0.0
				minutes[last_minute] += diff.seconds*last.rate
			else:
				if last_minute not in minutes:
					minutes[last_minute] = 0.0
				minutes[last_minute] += diff.seconds*last.rate
				
				
		last = cur
	
	for k in minutes:
		minutes[k] = minutes[k] / days_total
	
	return minutes
	
	
	last = None
	for i in sort:
		if last != None:
			en = (i.time-last.time).seconds * last.rate
			weighted.append(nt(last.time, en))
		last = i
	
	group = itertools.groupby(weighted, key)
	grouped = {}
	for k, g in group:
		grouped[k] = list(g)
	return grouped

def plot(x, y, xlab, ylab, tit, bar):
	plt.xlabel(xlab)
	plt.ylabel(ylab)
	plt.title(tit)
	if bar:
		plt.bar(x,y)
	else:
		plt.plot(x,y)
	plt.show()

def plot_weekday_avg(data, day):
	data = data[day]
	