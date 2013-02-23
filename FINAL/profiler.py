import datetime
import utils
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import namedtuple as NT

weekday_names = {0:'monday', 1:'tuesday', 2:'wednesday',3:'thursday',4:'friday',5:'saturday',6:'sunday'}


base_tuple = NT('base', ['time', 'rate'])

def str_to_tuple(val):
	split = val.strip().split(';')
	dt = datetime.datetime.strptime(split[0], '%Y-%m-%d %H:%M:%S')
	v = float(split[1])
	return base_tuple(dt, v)
	
def make(dataman, device, day, temp, cond, daytype):
	man = ProfileManager(dataman, device)
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
	def __init__(self, dataman, device):
		self.profiles = {}
		self.dataman = dataman
		self.device = device
	
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
					weights[g][m].append(profile.get_data()[m][0])
				weights[g][m] = float(numpy.std(weights[g][m]))
		sums = [0.0 for i in xrange(1440)]
		for g in weights:
			for m in xrange(1440):
				sums[m] += weights[g][m]
				if sums[m] == 0:
					print m
		
		for g in weights:
			for m in xrange(1440):
				weights[g][m] = weights[g][m] / sums[m]
		
		result = [(0.0, 0.0) for i in xrange(1440)]

		for p in profiles:
			for m in xrange(1440):
				data = p.get_data()[m]
				weight = weights[p.group][m]
				newtup = (result[m][0] + data[0] * weight, result[m][1] + data[1] * weight)
				result[m] = newtup
		return result
	
	def get_profile_def(self, a_date):
		weather = self.dataman.weather.collect(a_date)
		holiday = 'holiday' if self.dataman.holiday.check(a_date) else 'workday'
		weekday = weekday_names[a_date.weekday()]
		if weather.temp < -40:
			temp = '-100--40'
		elif weather.temp >= 40:
			temp = '40-100'
		else:
			low = weather.temp - weather.temp % 5
			high = low + 5
			temp = str(low) + '-' + str(high)
		
		for cond in weather.conditions:
			if 'cloudy' in cond:
				return [holiday, weekday, temp, 'cloudy']
			elif 'rain' in cond:
				return [holiday, weekday, temp, 'rain']
			elif 'snow' in cond:
				return [holiday, weekday, temp, 'snow']
			elif 'clear' in cond:
				return [holiday, weekday, temp, 'clear']
		return [holiday, weekday, temp]
	
	def plot(self, query, conf_int=False):
		result = self.calculate(query)
		
		fig, ax = plt.subplots(1)
		fig.autofmt_xdate()
		# group by minute of day, do autocounting
		x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), range(1440))
		y = map(lambda i: i[0], result)
		if conf_int:
			c_low = map(lambda i: i[0] - i[1], result)
			c_high = map(lambda i: i[0] + i[1], result)
			ax.fill_between(x, c_low, c_high, alpha=0.5, lw=0, color='yellow')
		
		ax.plot(x, y)
		ax.fmt_xdata = mdates.DateFormatter('%H:%M')
		ax.grid(True, which='major')
		plt.xlabel(u'Tid')
		plt.ylabel(u'Energianvändning')
		plt.title(u' '.join(query))
		plt.show()
	def diff_profiles(self, q1, q2):
		res1 = self.calculate(q1)
		res2 = self.calculate(q2)
		
		fig, ax = plt.subplots(1)
		fig.autofmt_xdate()
		# group by minute of day, do autocounting
		x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), range(1440))
		res1 = map(lambda i: i[0], res1)
		res2 = map(lambda i: i[0], res2)
		
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
	def diff_actual(self, date, conf_int=False):
		if date >= datetime.date.today():
			raise ValueError('invalid date')
		prof_def = self.get_profile_def(date)
		prof_res = self.calculate(prof_def)
		date_res = self.dataman.collectByDate(self.device, date)
		date_res = utils.collect_total(map(str_to_tuple, date_res), True)
		date_res = [((0.0, 0.0) if i not in date_res else date_res[i]) for i in range(1440)]
		
		fig, ax = plt.subplots(1)
		fig.autofmt_xdate()
		# group by minute of day, do autocounting
		x = map(lambda i: datetime.datetime(2012, 10, 12, i/60, i%60), range(1440))
		if conf_int:
			c_low = map(lambda i: i[0] - i[1], prof_res)
			c_high = map(lambda i: i[0] + i[1], prof_res)
			ax.fill_between(x, c_low, c_high, alpha=0.5, lw=0, color='yellow')
		
		prof_res = map(lambda i: i[0], prof_res)
		date_res = map(lambda i: i[0], date_res)
		
		ax.fill_between(x, prof_res, date_res, color='blue', lw=0, alpha=0.6)
		ax.plot(x, prof_res, color='red', lw=0.8)
		ax.plot(x, date_res, color='green', lw=0.8)
		ax.plot(x, [numpy.mean(prof_res)]*1440, color='red', lw=1)
		ax.plot(x, [numpy.mean(date_res)]*1440, color='green', lw=1)
		ax.fmt_xdata = mdates.DateFormatter('%H:%M')
		ax.grid(True, which='major')
		plt.xlabel(u'Tid')
		plt.ylabel(u'Energianvändning')
		t1 = u' '.join(prof_def) + ' (red)'
		t2 = str(date) + u' (green)'
		plt.title(t1 + ' and ' + t2)
		plt.show()
		
class DayProfile(Profile):
	def __init__(self, weekday, group):
		Profile.__init__(self, weekday_names[weekday], group)
		self.weekday = weekday

class TemperatureProfile(Profile):
	pass # use default profile

class ConditionProfile(Profile):
	pass # use default profile

class DayTypeProfile(Profile):
	pass # use default profile
