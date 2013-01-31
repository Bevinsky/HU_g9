'''
Created on 26 jan 2013

@author: Bevin
'''

import csv
from collections import namedtuple as nt
import random
import datetime

#formats are at:
# http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

class CSVReader(object):
    """
    This class parses a CSV file according to a set of parameters and gives
    a list of tuples with the parsed data. It can be iterated on with a for
    statement, and also converted into a list with list().
    
    Arguments:
                filename - the filename of the csv file
                
                delimiter - the delimiter that separates columns in the file
                
                header - whether or not the file has a header. If this is true,
                         the first row will be selected as a header and used
                         to create a collections.namedtuple for the data results.
                
                *_format - the formats to parse datetime.datetime, datetime.date
                           and datetime.time values with.
    
    One way of using this efficiently is to first load all the rows into a list,
    and then filtering with lambdas:
    
        >>> import csvreader.CSVReader as CSVReader
        >>> import math
        >>> all_rows = CSVReader('data/stockholm_timmedel.csv', delimiter=';', header=True)
        >>> all_rows = list(all_rows)
        >>> mondays = filter(lambda r: r.datum.weekday() == 0 and not math.isnan(r.timmedel), all_rows)
    
    Keep in mind to save the original dataset in memory, so that there isn't
    too much disk activity; it's slow if the csv file is large.
    """
    def __init__(self, filename, delimiter=',', header=True,
                 date_format='%Y-%m-%d', time_format='%H:%M:%S',
                 datetime_format='%Y-%m-%d %H:%M:%S'):
        self.file = open(filename, 'rb')
        self.reader = csv.reader(self.file, delimiter=delimiter)
        self.delimiter = delimiter
        self.has_header = header
        self.header_found = False
        
        self.datetime_format = datetime_format
        self.date_format = date_format
        self.time_format = time_format
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.has_header and not self.header_found:
            #assume the first row is the header
            r = self.reader.next()
            #make it alpha and lowercase only
            r = map(lambda item: ''.join(ch for ch in item if ch.isalpha()).lower(), r)
            #generate a random name
            tuplename = hex(random.getrandbits(24))[1:]
            #make a named tuple with the header as parameter names
            self.tuplecreator = nt(tuplename, r)
            self.header_found = True
        
        row = self.reader.next()
        #run our type converter on it
        row = map(self.converter, row)
        
        if self.has_header:
            #for some reason namedtuple and tuple don't have the same
            #constructor...? how annoying
            return self.tuplecreator(*row)
        else:
            return tuple(row)
    
    def converter(self, value):
        #test: datetime, date, time, float/int
<<<<<<< HEAD
=======
        value = value.replace('"' , '')
>>>>>>> origin/bevin
        try:
            conv = datetime.datetime.strptime(value, self.datetime_format)
            return conv
        except ValueError:
            pass
        try:
            conv = datetime.datetime.strptime(value, self.date_format)
            return conv.date()
        except ValueError:
            pass
        try:
            conv = datetime.datetime.strptime(value, self.time_format)
            return conv.time()
        except ValueError:
            pass
        try:
            conv = float(value.replace(',', '.'))
            return conv
        except ValueError:
            pass
        
        #no conversion possible
        return value

def test():
    read = CSVReader("data/stockholm_timmedel.csv", delimiter=';', header=True)
    i = 0
    for row in read:
        if i > 10:
            break
        yield row
        i += 1
