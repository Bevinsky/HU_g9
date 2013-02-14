import datetime
import utils
import numpy

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
			day.process_data(dataman.collect_by_day(device, day.weekday))
		
		man.add_group(daygr)
	
	if temp:
		tempgr = ProfileGroup('temperature')
		
		tp = TemperatureProfile('-100--40', tempgr)
		tp.process_data(dataman.collect_by_temperature(device, (-100, -40)))
		
		for v in xrange(-40, 35, 5):
			tp = TemperatureProfile(str(v) + '-' + str(v+5), tempgr)
			tp.process_data(dataman.collect_by_temperature(device, (v, v+5)))
		
		tp = TemperatureProfile('40-100', tempgr)
		tp.process_data(dataman.collect_by_temperature(device, (40, 100)))
		man.add_group(tempgr)
	
	if cond:
		condgr = ProfileGroup('condition')
		
		conds = []
		conds.append(ConditionProfile('cloudy', condgr))
		conds.append(ConditionProfile('rain', condgr))
		conds.append(ConditionProfile('clear', condgr))
		conds.append(ConditionProfile('snow', condgr))
		
		for c in conds:
			conds.process_data(dataman.collect_by_condition(device, [c.name]))
		
		man.add_group(condgr)
	
	if daytype:
		daytypegr = ProfileGroup('daytype')
		
		reg = DayTypeProfile('weekday', daytypegr)
		hol = DayTypeProfile('holiday', daytypegr)
		
		man.add_group(daytypegr)
		
	return man


class Profile(object):
	def __init__(self, name, group):
		self.name = name
		self.group = group
		self.group.add_profile(self)
	
	def get_data(self):
		return self.data
	
	def process_data(self, data):
		data = utils.collect_total(day, True)
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
