'''
Created on 26 jan 2013

@author: Bevin
'''

import csvreader
import itertools
import math

all_lines = []
valid_lines = []

def load():
    global all_lines, valid_lines
    reader = csvreader.CSVReader('data/stockholm_timmedel.csv', delimiter=';', header=True)
    all_lines = list(reader)
    valid_lines = filter(lambda x: not math.isnan(x.timmedel), all_lines)

def groupby(key, use_all_data=False):
    """
    An example of using itertools to group results on a key.
    
        Arguments:
                    key - function to select key with
                    
                    use_all_data - if True, the grouping will include invalid
                                   temp values (like nan)
    """
    
    #groupby needs the data to be sorted
    data = all_lines if use_all_data else valid_lines
    sorted_data = sorted(data, key=key)
    groupby = itertools.groupby(sorted_data, key)
    
    complete = {}
    
    # this dict contains the data grouped by the keys
    for k, g in groupby:
        complete[k] = list(g)
    
    return complete
    





