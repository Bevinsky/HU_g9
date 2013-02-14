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
	
	gr.add_profile(mo)
	gr.add_profile(tu)
	gr.add_profile(we)
	gr.add_profile(th)
	gr.add_profile(fr)
	gr.add_profile(sa)
	gr.add_profile(su)
	
	for p in gr.profiles:
		gr.profiles[p].process_data(data)
	
	man = ProfileManager()
	man.add_group(gr)
	return man
	



class Profile(object):
	def __init__(self, name, group):
		self.name = name
		self.group = group
		self.group.add_profile(self)
	
	def get_data(self):
		return self.data
	
	def process_data(self, data):
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

"""
class ProfileManager(object):
	def __init__(self):
		self.profiles = {}
	
	def add(self, p):
		if p.selector not in self.profiles:
			self.profiles[p.selector] = p
	
	def get(self, profile_list):
		profiles = map(lambda p: self.profiles[p], profile_list)
		types = []
		for pr in profiles:
			if type(pr) in types:
				raise ValueError("too many profiles of the same type")
			types.append(type(pr))
		
		total = dict((i, 0.0) for i in xrange(1440))
		counts = dict((i, 0) for i in xrange(1440))
		for k in total:
			for pr in profiles:
				if k in pr.data:
					total[k] += pr.data[k] * pr.weighter(k)
					counts[k] += 1
			total[k] = total[k] / counts[k]
		
		return total

class Profile(object):
	def __init__(self, selector, group=None, weighter=0.0):
		'''
		data: 		a data set with attributes `time` and `rate`, where `time` is a
					datetime.datetime and rate is a float or int.
		
		selector:	the name of the profile, such as 'monday' or 'temp_group_5'.
		
		group:		the group of the profile, such as 'weekday' or 'temp'.
					no profile evaluation can have more than one profile from
					the same group.
		
		continuous:	if True, the data is time-continuous, and autocounting will
					be used for the data parsing.
		
		weighter:	a weighting function. can also be a function.
		'''
		self.grid_dim = (1440, 1500) # 3000 W, 2 W per cell
		self.data_grid = []
		self.selector = selector
		self.group = group
		if not isinstance(weighter, func):
			def w_func(grp):
				return weighter
			self.weighter = w_func
		
	def process_data(self, data):
		pass

class DayProfile(Profile):
	def __init__(self, data, selector, weekday):
		Profile.__init__(self, selector, 'days', 0)
		self.weekday = weekday
		self.process_data(data)
	
	def process_data(self, data):
		average = utils.collect_total(data, False)
		for a in average:
			average[a] = numpy.mean(average[a])
		day = utils.groupby(data, xkey=lambda x: x.time.weekday() == self.weekday)[self.weekday]
		day = utils.collect_total(day, True)
		for a in day:
			day[a] = numpy.mean(day[a])
		
		self.data = day
		
class WeekdayProfile(Profile):
	def __init__(self, profiles, selector):
		Profile.__init__(self, selector, 'weekdays', 0)
		self.profiles = profiles
		self.process_data(None)
	
	def process_data(self, data):
		self.data = {}
		counts = {}
		
		for pr in self.profiles:
			for k in pr.data:
				if k not in self.data:
					self.data[k] = 0
					self.counts[k] = 0
				self.data[k] += pr.data[k]
				counts[k] += 1
		for k in self.data:
			self.data[k] = self.data[k] / counts[k]
		
		
"""