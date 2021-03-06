﻿import datetime
import utils
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import namedtuple as NT

weekday_names = {0:'monday', 1:'tuesday', 2:'wednesday',3:'thursday',4:'friday',5:'saturday',6:'sunday'}

def make_test1(data):
	gr = ProfileGroup('weekdays')
	mo = DayProfile(0, gr)
	tu = DayProfile(1, gr)
	we = DayProfile(2, gr)
	th = DayProfile(3, gr)
	fr = DayProfile(4, gr)
	sa = DayProfile(5, gr)
	su = DayProfile(6, gr)
	
	for p in gr.profiles:
		gr.profiles[p].process_data(data)
	
	
	
	
	man = ProfileManager()
	man.add_group(gr)
	return man

base_tuple = NT('base', ['time', 'rate'])

def str_to_tuple(val):
	split = val.split(';')
	dt = datetime.datetime.strptime(split[0], '%Y-%m-%d %H:%M:%S')
	v = float(split[1])
	return base_tuple(dt, v)
	
def make(dataman, device, day, temp, cond, daytype):
	man = ProfileManager()
	if day:
		daygr = ProfileGroup('weekday')
		
		days = []
		days.append(DayProfile(0, daygr))
		days.append(DayProfile(1, daygr))
		days.append(DayProfile(2, daygr))
		days.append(DayProfile(3, daygr))
		days.append(DayProfile(4, daygr))
		days.append(DayProfile(5, daygr))
		days.append(DayProfile(6, daygr))
		
		for day in days:
			day.process_data(map(str_to_tuple, dataman.collectByWeekday(device, day.weekday)))
		
		man.add_group(daygr)
		print "Added weekday"
	
	if temp:
		tempgr = ProfileGroup('temperature')
		
		tp = TemperatureProfile('-100--40', tempgr)
		tp.process_data(map(str_to_tuple, dataman.collectByTemp(device, (-100, -40))))
		
		for v in xrange(-40, 35, 5):
			tp = TemperatureProfile(str(v) + '-' + str(v+5), tempgr)
			tp.process_data(map(str_to_tuple, dataman.collectByTemp(device, (v, v+5))))
		
		tp = TemperatureProfile('40-100', tempgr)
		tp.process_data(map(str_to_tuple, dataman.collectByTemp(device, (40, 100))))
		man.add_group(tempgr)
		print "Added temp"
	
	if cond:
		condgr = ProfileGroup('condition')
		
		conds = []
		conds.append(ConditionProfile('cloudy', condgr))
		conds.append(ConditionProfile('rain', condgr))
		conds.append(ConditionProfile('clear', condgr))
		conds.append(ConditionProfile('snow', condgr))
		
		for c in conds:
			c.process_data(map(str_to_tuple, dataman.collectByConditions(device, [c.name])))
		
		man.add_group(condgr)
		print "Added cond"
	
	if daytype:
		daytypegr = ProfileGroup('daytype')
		
		reg = DayTypeProfile('workday', daytypegr)
		reg.process_data(map(str_to_tuple, dataman.collectByWorkdays(device)))
		hol = DayTypeProfile('holiday', daytypegr)
		hol.process_data(map(str_to_tuple, dataman.collectByHoliday(device)))
		
		man.add_group(daytypegr)
		print "Added daytype"
		
	return man


class Profile(object):
	def __init__(self, name, group):
		self.name = name
		self.group = group
		self.group.add_profile(self)
	
	def get_data(self):
		return self.data
	
	def process_data(self, data):
		data = utils.collect_total(data, True)
		self.data = data
	
class ProfileGroup(object):
	def __init__(self, name):
		self.name = name
		self.profiles = {}
	
	def add_profile(self, profile):
		if profile.name not in self.profiles:
			self.profiles[profile.name] = profile


class ProfileManager(object):
	def __init__(self):
		self.profiles = {}
	
	def add_profile(self, p):
		if p.name not in self.profiles:
			self.profiles[p.name] = p
	
	def add_group(self, g):
		for pname in g.profiles:
			self.add_profile(g.profiles[pname])
	
	def calculate(self, query):
		profiles = map(lambda x: self.profiles[x], query)
		groups = []
		weights = {}
		for p in profiles:
			# get groups
			if p.group in groups:
				raise ValueError("too many profiles of the same type")
			groups.append(p.group)
		for g in groups:
			# get weighting
			weights[g] = []
			for m in xrange(1440):
				weights[g].append([])
				for pkey in g.profiles:
					profile = g.profiles[pkey]
					weights[g][m].append(profile.get_data()[m])
				weights[g][m] = float(numpy.std(weights[g][m]))
		sums = [0.0 for i in xrange(1440)]
		for g in weights:
			for m in xrange(1440):
				sums[m] += weights[g][m]
		
		for g in weights:
			for m in xrange(1440):
				weights[g][m] = weights[g][m] / sums[m]
		
		result = [0.0 for i in xrange(1440)]

		for p in profiles:
			for m in xrange(1440):
				result[m] += p.get_data()[m] * weights[p.group][m]
		
		return result
	
	def plot(self, query):
		result = self.calculate(query)
		
		fig, ax = plt.subplots(1)
		fig.autofmt_xdate()
		# group by minute of day, do autocounting
		x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), range(1440))
		y = result
		
		ax.plot(x, y)
		ax.fmt_xdata = mdates.DateFormatter('%H:%M')
		ax.grid(True, which='major')
		plt.xlabel(u'Tid')
		plt.ylabel(u'Energianvändning')
		plt.title(u' '.join(query))
		plt.show()
	def diff(self, q1, q2):
		res1 = self.calculate(q1)
		res2 = self.calculate(q2)
		
		fig, ax = plt.subplots(1)
		fig.autofmt_xdate()
		# group by minute of day, do autocounting
		x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), range(1440))
		
		ax.fill_between(x, res1, res2, color='blue', lw=0, alpha=0.6)
		ax.plot(x, res1, color='red', lw=0.8)
		ax.plot(x, res2, color='green', lw=0.8)
		ax.fmt_xdata = mdates.DateFormatter('%H:%M')
		ax.grid(True, which='major')
		plt.xlabel(u'Tid')
		plt.ylabel(u'Energianvändning')
		t1 = u' '.join(q1) + ' (red)'
		t2 = u' '.join(q2) + ' (green)'
		plt.title(t1 + ' and ' + t2)
		plt.show()
		
class DayProfile(Profile):
	def __init__(self, weekday, group):
		Profile.__init__(self, weekday_names[weekday], group)
		self.weekday = weekday
	
	def get_data(self):
		return self.data
	
	def process_data(self, data):
		# all data is not grouped?
		day = utils.groupby(data, xkey=lambda x: x.time.weekday())[self.weekday]
		day = utils.collect_total(day, True)
		for m in day:
			day[m] = day[m] # watt i medel
		
		self.data = day


class TemperatureProfile(Profile):
	pass # use default profile

class ConditionProfile(Profile):
	pass # use default profile

class DayTypeProfile(Profile):
	pass # use default profile
