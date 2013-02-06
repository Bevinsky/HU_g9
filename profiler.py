import datetime
import utils



class Profile(object):
	def __init__(self, data, selector, group=None, continuous=True, weighter=0.0):
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
		
		self.process_data(data)
		
	def process_data(self, data):
		pass

