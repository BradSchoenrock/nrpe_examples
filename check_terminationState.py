#!/usr/bin/python

################################################################
# Script to check the terminationState on Stichers 
# This script will be used as an NRPE plugin for ICINGA monitoring
#
# Revision History:
# 	Version: 1.0
# 	Date:    2018-08-27
################################################################


import os, getopt, sys
from datetime import datetime

try:
	opts, args = getopt.getopt(sys.argv[1:], "w:c:s:h:", ["warning=", "critical=", "state=", "hours="])
except getopt.GetoptError as err:
	print str(err)
	print "Usage :",sys.argv[0]," [-w|--warning]<count> [-c|--critical]<count> [-s|--state]<statename> [-h|--hours]<hours>"
	exit(4)

for o, a in opts:
	if o in ("-w", "--warning"):
		warningThreshold = int(a) 
	elif o in ("-c", "--critical"):
		criticalThreshold = int(a)
	elif o in ("-s", "--state"):
		termState = a.rstrip('\n')
	elif o in ("-h", "--hours"):
		hourBack = int(a)
	else:
		pass

termStateCount = 0;
cmd = "grep terminationState /var/log/cloudtv.log | grep "+termState+" > /tmp/terminationState.out"
os.system(cmd)

termStatsFile = open("/tmp/terminationState.out", "r")
StbActivityAckTimeout = AppEngineCommunicationFl = SrmBandwidthUnavailable = 0

for line in termStatsFile:
	stateArray = line.split()
	logTime = datetime.strptime(stateArray[0],"%Y-%m-%dT%H:%M:%S.%f+00:00")
	timeNow = datetime.utcnow()
        timeDiff = timeNow - logTime;
	totalSeconds = (timeDiff.microseconds + 0.0 + (timeDiff.seconds + timeDiff.days * 24 * 3600) * 10 ** 6) / 10 ** 6
	hourDiff = int(totalSeconds/60/60)
	if hourDiff <= hourBack:
		termStateCount = termStateCount + 1;

if termStateCount >= criticalThreshold:
        print "CRITICAL - terminationState ",termState,termStateCount
	exit(2)

if termStateCount >= warningThreshold: 
	print "WARNING - terminationState ",termState,termStateCount
	exit(1)

if termStateCount < warningThreshold:
	print "OK - terminationState ",termState,termStateCount
	exit(0) 
