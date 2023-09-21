import time
from datetime import datetime
from os.path import exists
import os

class Logger():
  def __init__(self, logfile='log.txt', module='', log_level = 1):
    if (not logfile.endswith('.py')):
      self.logfile = logfile
      self.loglevel = log_level
    else:
      self.logfile = 'log.txt'
    self.module = module
    self.lastLog = ''
    self.repeatedLogCount = 0

  def Reset(self):
    logtext = None
    try:
      os.replace(self.logfile, self.logfile.replace('.txt', '.bak.txt'))
    except Exception as error:
      logtext = 'Exception caught while trying to replace logfile %s. %s'%(self.logfile, repr(error))
      print(logtext)
    with open (self.logfile, 'w') as f:
      if (logtext):
        f.write(logtext)
      t = time.localtime(datetime.timestamp(datetime.now()))
      stime=time.strftime("%d/%m/%Y %H:%M:%S", t)
      f.write('%s:Init\n'%(stime))

  def write(self, text, linenumber = -1):
    if (not exists(self.logfile)):
      self.Reset()
    logstring = ''
    do_print = True
    if (self.lastLog == text):
      if (self.repeatedLogCount < 5):
        do_print = True
      else:
        do_print = False
        # trying to log the same thing, just count instead
      self.repeatedLogCount += 1
    else:
      if (self.repeatedLogCount > 0):
        logstring = 'Repeated %d times.\n'%self.repeatedLogCount
      self.repeatedLogCount = 0

    if (do_print):
      t = time.localtime(datetime.timestamp(datetime.now()))
      stime=time.strftime("%d/%m/%Y %H:%M:%S", t)
      logstring += '(%s),(%s:%d):%s\n'%(stime, self.module, linenumber, text)
      with open (self.logfile, 'a') as f:
        f.write(logstring)
      if (self.loglevel >= 1):
        print(logstring.replace('\n',''))
    self.lastLog = text
  
  def log(self, text, linenumber = -1):
    self.write(text, linenumber)
  
  def Log(self, text, linenumber = -1):
    self.write(text, linenumber)
	
  def Write(self, text, linenumber = -1):
    self.write(text, linenumber)


