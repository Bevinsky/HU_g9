﻿import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy
import itertools
from collections import namedtuple as NT
import datetime
import scipy

def total_avg(total):
	total = sorted(total, key=lambda x: x.time)
	fig, ax = plt.subplots(1)
	fig.autofmt_xdate()
	# group by minute of day, do autocounting
	minutes = collect_total(total, False)
	x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), minutes.keys())
	
	y = []
	for i in minutes:
		y.append(minutes[i]/60)
	
	ax.plot(x, y)
	ax.fmt_xdata = mdates.DateFormatter('%H:%M')
	ax.grid(True, which='major')
	plt.xlabel(u'Tid')
	plt.ylabel(u'Effekt i medel')
	plt.title(u'Effektförbrukning över ett dygn')
	plt.show()

def mean_confidence_interval(data, confidence=0.95):
	a = 1.0*numpy.array(data)
	n = len(a)
	m, se = numpy.mean(a), scipy.stats.stderr(a)
	h = se * scipy.stats.t._ppf((1+confidence)/2., n-1)
	return m, h

def intensity(total):
	total = sorted(total, key=lambda x: x.time)
	grp = plot_grouped(total, lambda x: x.time.weekday())
	alpha = 1.0/len(grp)
	min_ = 0
	for k in grp:
		min_ = min(min(grp[k]), min_)
	fig, ax = plt.subplots(1)
	fig.autofmt_xdate()
	
	average = {}
	x = []
	for k in grp:
		# group by minute of day, count days manually
		minutes = collect_total(grp[k], True)
		x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), minutes.keys())
		
		y = []
		for i in minutes:
			y.append(minutes[i])
		
		for mk in minutes:
			if mk not in average:
				average[mk] = 0.0
			average[mk] += minutes[mk]
		
		ax.fill_between(x, y, lw=0, alpha=alpha)
	
	x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), average.keys())
	y = []
	for i in average:
		y.append(average[i]/len(grp))
	ax.plot(x,y,'r', lw=0.5)
	
	ax.fmt_xdata = mdates.DateFormatter('%H:%M')
	ax.grid(True, which='major')
	plt.xlabel(u'Tid')
	plt.ylabel(u'Medeleffekt i watt')
	plt.title(u'Intensitetsgraf')
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

def groupby(data, xkey=lambda x: x, ykey=lambda y: y):
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

def weighted_mean(data, weight=1):
	pass

def collect_total(total, count_days=False):
	
	if not total:
		return dict(((i, 0) for i in xrange(1440)))
	
	
	sort = sorted(total, key=lambda t:t.time)
	first_day = sort[0]
	last_day = sort[-1]
	days_total = (last_day.time-first_day.time).days
	weighted = []
	nt = NT('energytuple', ['time', 'energy'])
	
	minutes = {}
	
	last = None
	last_gap = None
	c = 0
	cur = None # scope
	temp_minute = 0
	for cur in sort:
		if not last_gap:
			last_gap = cur
		if last:
			last_minute = last.time.minute + last.time.hour*60
			cur_minute = cur.time.minute + cur.time.hour*60
			diff = cur.time-last.time
			if diff.days >= 1:				
				c += (last.time-last_gap.time).days + 1
				#print (last.time-last_gap.time).days + 1
				last_gap = cur
				last = cur
				continue
			if last_minute != cur_minute:
				remain = 60 - last.time.second
				temp_minute += remain*last.rate
				if last_minute not in minutes:
					minutes[last_minute] = []
				minutes[last_minute].append(temp_minute/60.0)
				temp_minute = 0
				diff -= datetime.timedelta(0, remain)
				while diff.seconds >= 60:
					last_minute += 1
					if last_minute >= 1440:
						last_minute = 0
					if last_minute not in minutes:
						minutes[last_minute] = []
					minutes[last_minute].append(last.rate)
					diff -= datetime.timedelta(0, 60)
				last_minute += 1
				if last_minute >= 1440:
					last_minute = 0
				if last_minute not in minutes:
					minutes[last_minute] = []
				temp_minute += diff.seconds*last.rate
			else:
				if last_minute not in minutes:
					minutes[last_minute] = []
				temp_minute += diff.seconds*last.rate
				
				
		last = cur
	
	c += (last.time-last_gap.time).days + 1
	
	for k in minutes:
		conf_int = mean_confidence_interval(minutes[k])
		minutes[k] = (conf_int[0], conf_int[1])
	
	return minutes

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
	