#!/usr/bin/python

################################################################
# Script to check the DEGRADED status on CSM to see the degraded Stitchers 
# This script will be used as an NRPE plugin for ICINGA monitoring
#
# Revision History:
# 	Version: 1.0
# 	Date:    2018-08-27
# 	Version: 2.0
# 	Date:    2020-06-23
# 	Version: 2.0.1
# 	Date:    2020-10-16
################################################################

import os
import getopt
import sys
import time
import glob
import calendar

from datetime import datetime

def getdirfiles(pathtosearch):
	file_list = [fn for fn in glob.glob(pathtosearch)
  		if not os.path.basename(fn).endswith('.gz')]
	
	file_list.sort(reverse=True)  #sorting in descending order
	return file_list

def strip_list(str_list):
	"""[Take a list of string objects and return the same list stripped of extra whitespace]

	Args:
		str_list ([list]): [list of string objects]

	Returns:
		[list]: [list stripped of extra whitespace]
	"""
	str_list = [entry.strip() for entry in str_list]
	str_list = [entry.strip(',') for entry in str_list]
	return str_list

try:
	opts, args = getopt.getopt(sys.argv[1:], "w:c:s:h:", ["warning=", "critical=", "hours="])
except getopt.GetoptError as err:
	print str(err)
	print "Usage :",sys.argv[0]," [-w|--warning]<second(s)> [-c|--critical]<second(s)> [-h|--hours]<hours>"
	exit(3)

warning_threshold = 40
critical_threshold = 50
hour_back = 4

for option, argument in opts:
	if option in ("-w", "--warning"):
		warning_threshold = int(argument) 
	elif option in ("-c", "--critical"):
		critical_threshold = int(argument)
	elif option in ("-h", "--hours"):
		hour_back = int(argument)
	else:
		pass

files_list = getdirfiles('/var/log/cloudtv.log*')

# Added RegEx for DEGRADED or HEALTHY and .out file name
# Added -h (Suppress the prefixing of file names on output.) for the grep
pipeType =  ' > '
for afile in files_list:
	if os.path.isfile(afile):
		cmd = "grep -h -E 'DEGRADED|HEALTHY' " + afile + pipeType + "/tmp/DEGRADED_HEALTHY.out"
		pipeType = ' >> '
		os.system(cmd)

degradedFile = open("/tmp/DEGRADED_HEALTHY.out", "r")

start_time_dict = dict()
stop_time_dict = dict()
degraded_time_dict = dict()
healthy_time_dict = dict()
critical_threshold_dict = dict()
warning_threshold_dict = dict()

stitcher_ip = None

# Prototype code for getting ? hours back to compare with log file
time_now = round(time.time()) # seconds since the epoch, in UTC (int)
# convert hour_back into seconds
hoursbackinseconds = hour_back * 3600
start_search_time = time_now - hoursbackinseconds

for line in degradedFile:
	line_array = line.split()
	line_array = strip_list(line_array)
	log_time = datetime.strptime(line_array[0],"%Y-%m-%dT%H:%M:%S.%f+00:00")
	datetimeobj = datetime(log_time.year, log_time.month, log_time.day, log_time.hour, log_time.minute, log_time.second, log_time.microsecond)
	log_epoch = calendar.timegm(datetimeobj.timetuple())
	if (log_epoch >= start_search_time):
		# Check for the log entry that reports the current health #
		if 'health' in line_array[4]:
			# Check for UNHEALTHY and don't increment the stitcher count for a health log entry
			if 'UNHEALTHY' in line_array[11]:
				stitcher_ip = line_array[8].replace(":16668","")
				if stitcher_ip in start_time_dict:
					degraded_time_dict[stitcher_ip] = log_epoch
				else:
					start_time_dict[stitcher_ip] = log_epoch
			# Check for HEALTHY and reset stitcher count to zero
			elif 'HEALTHY' in line_array[11]:
				stitcher_ip = line_array[8].replace(":16668","")
				if stitcher_ip in start_time_dict:
					stop_time_dict[stitcher_ip] = log_epoch
					degraded_time = degraded_time_dict.get(stitcher_ip, None)
					# Cleanup degraded_time_dict if an entry is found
					if degraded_time != None:
						del degraded_time_dict[stitcher_ip]
			# Check for DEGRADED and don't increment the stitcher count for a health log entry
			elif 'DEGRADED' in line_array[11]:
				stitcher_ip = line_array[8].replace(":16668","")
		# If it's not a log entry for current health then it's a DEGRADED only log entry so, save degraded stitcher ipaddress and adjust count
		elif 'DEGRADED' in line_array[14]:
			stitcher_ip = line_array[6].replace(":16668","")
			if stitcher_ip in start_time_dict:
				degraded_time_dict[stitcher_ip] = log_epoch
			else:
				start_time_dict[stitcher_ip] = log_epoch
		elif 'UNHEALTHY' in line_array[23]:
			stitcher_ip = line_array[15].replace(":16668","")
			if stitcher_ip in start_time_dict:
				degraded_time_dict[stitcher_ip] = log_epoch
			else:
				start_time_dict[stitcher_ip] = log_epoch
	else:
		# Outside of window for processing - do nothing
		pass

for key in start_time_dict:
	if key in stop_time_dict:
		time_diff = stop_time_dict[key] - start_time_dict[key]
		healthy_time_dict[key] = str(time_diff)
	else:
		time_diff = degraded_time_dict[key] - start_time_dict[key]
		if time_diff > critical_threshold:
			critical_threshold_dict[key] = str(time_diff)
			continue
		if time_diff > warning_threshold:
			warning_threshold_dict[key] = str(time_diff)

# Cleanup temporary file in /tmp
file_path = '/tmp/DEGRADED_HEALTHY.out'
try:
	os.remove(file_path)
except:
	print "UNKNOWN - Error while deleting file ", file_path
	exit(3)

if critical_threshold_dict:
	print "CRITICAL - below Stitcher(s) are Degraded. Critical Threshold is", str(critical_threshold), 'second(s)'
	for key in critical_threshold_dict:
		print key, 'is currently degraded for at least', critical_threshold_dict[key], 'second(s)'
	exit(2)
elif warning_threshold_dict:
	print "WARNING - below Stitcher(s) are Degraded. Warning Threshold is", str(warning_threshold), 'second(s)'
	for key in warning_threshold_dict:
		print key, 'is currently degraded for at least', warning_threshold_dict[key], 'second(s)'
	exit(1)
else:
	print "OK - No Stitchers violated the Degraded Threshold"
	for key in healthy_time_dict:
		print key, 'was degraded for ', healthy_time_dict[key], 'second(s),', 'now Healthy.'
	exit(0) 
