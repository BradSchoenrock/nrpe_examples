#!/usr/bin/python

################################################################
#Script to check the logstash logs for ""type"=>"cluster_block_exception", "reason""
#
#
# Revision History:
#       Version: 1.0
#       Date:    2020-08-26
################################################################
#

import os, getopt, sys
from datetime import datetime

try:
        opts, args = getopt.getopt(sys.argv[1:], "w:c:s:h:", ["warning=", "critical=", "state=", "hours="])
except getopt.GetoptError as err:
        print str(err)
        print "Usage :",sys.argv[0]," [-w|--warning]<count> [-c|--critical]<count> [-s|--state]<statename> [-h|--hours]<hours>"
        exit(4)

hourBack = 1
criticalThreshold = 1
warningThreshold = 1
termState = 0

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
cmd = "grep cluster_block_exception /var/log/logstash/logstash-plain.log > /tmp/logstash.out"
os.system(cmd)

termStatsFile = open("/tmp/logstash.out", "r")
StbActivityAckTimeout = AppEngineCommunicationFl = SrmBandwidthUnavailable = 0

for line in termStatsFile:
        stateArray = line.split()
        stateArray = stateArray[0].replace('[INFO', '')
        print(stateArray)
 #      print(stateArray[0])
        stateArray = stateArray.replace('[', '')
        stateArray = stateArray.replace(']', '')
        logTime = datetime.strptime(stateArray,"%Y-%m-%dT%H:%M:%S,%f")
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

