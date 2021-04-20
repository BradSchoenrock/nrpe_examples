#!/usr/bin/python

################################################################
# Script to check the "ERR lsm" and "unhealthy" 
# This script will be used as an NRPE plugin for ICINGA monitoring
#
# Revision History:
# 	Version: 1.0
# 	Date:    2018-08-31
################################################################


import os, getopt, sys
from datetime import datetime

try:
	opts, args = getopt.getopt(sys.argv[1:], "w:c:s:m:", ["warning=", "critical=", "minutes="])
except getopt.GetoptError as err:
	print str(err)
	print "Usage :",sys.argv[0]," [-w|--warning]<count> [-c|--critical]<count> [-m|--minutes]<hours>"
	exit(4)

for o, a in opts:
	if o in ("-w", "--warning"):
		warningThreshold = int(a) 
	elif o in ("-c", "--critical"):
		criticalThreshold = int(a)
	elif o in ("-m", "--minutes"):
		minsBack = int(a)
	else:
		pass

lsmUnhealthyCount = 0;
cmd = "grep \"ERR lsm\" /var/log/cloudtv.log | grep -i \"unhealthy\" > /tmp/lsm_unhealthy.out"
os.system(cmd)

lsmUnhealthyFile = open("/tmp/lsm_unhealthy.out", "r")

for line in lsmUnhealthyFile:
	lsmUnhealthyArray = line.split()
	logTime = datetime.strptime(lsmUnhealthyArray[0],"%Y-%m-%dT%H:%M:%S.%f+00:00")
	timeNow = datetime.utcnow()
        timeDiff = timeNow - logTime;
	totalSeconds = (timeDiff.microseconds + 0.0 + (timeDiff.seconds + timeDiff.days * 24 * 3600) * 10 ** 6) / 10 ** 6
	minsDiff = int(totalSeconds/60)
	if minsDiff <= minsBack:
        	lsmUnhealthyCount = lsmUnhealthyCount + 1;

if lsmUnhealthyCount >= criticalThreshold:
        print "CRITICAL - lsm unhealthy count is",lsmUnhealthyCount
        exit(2)

if lsmUnhealthyCount >= warningThreshold:
        print "WARNING - lsm unhealthy count is",lsmUnhealthyCount
        exit(1)

if lsmUnhealthyCount < warningThreshold:
        print "OK -  lsm unhealthy count is",lsmUnhealthyCount
        exit(0)

