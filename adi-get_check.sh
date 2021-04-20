#!/bin/bash

USAGE="$(basename "$0") [-w|--warning]<minutes> [-c|--critical]<minutes>"

# print usage
if [[ $# -lt 4 ]]
then
	echo ""
	echo "Wrong Syntax: $(basename "$0") $*"
	echo ""
	echo "Usage: $USAGE"
	echo ""
	exit 4
fi
# read input
while [[ $# -gt 0 ]]
  do
        case "$1" in
               -w|--warning)
               shift
               warning=$1
        ;;	
	       -c|--critical)
               shift
               critical=$1
        ;;
        esac
        shift
  done

TEMPFILE="/tmp/adi-status_nrpe.txt"
LOG="/var/log/adi-trailers.log"
LOCKTIME=0

# first time run, if no status file
if [ -e "$TEMPFILE" ]; then
	:	
else
	$(touch /tmp/adi-status_nrpe.txt)
fi

source $TEMPFILE
# If file was locked during previous run, increment the time the adi-get script has been locked.
if [[ $STATUS == *"locked"*"minutes"* ]]; then
 LOCKTIME=$(echo $STATUS | cut -d' ' -f2)
fi

if sudo test -e "/var/lock/adi-trailers/adi-get.lock"; then
	LOCKTIME=$((LOCKTIME + 5))
	STATUS="locked $LOCKTIME minutes"
	if [[ $LOCKTIME -ge $critical ]]; then
		echo "CRITICAL - adi-get is locked for $LOCKTIME minutes"
		echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
		exit 2
	elif [[ $LOCKTIME -ge $warning ]]; then
		echo "WARNING - adi-get is locked for $LOCKTIME minutes"
		echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
		exit 1
	else
		echo "OK - adi-get is locked for $LOCKTIME minutes, It is less than the thresholds"
		echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
		exit 0
	fi
else
	TAIL="$(tail -n 1 $LOG)"
 	if [[ $TAIL == *"Unknown error fetching files. Exiting"* ]]; then
  		STATUS="ADI INGEST FAILED"
		echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
		echo "CRITICAL - $STATUS"
		exit 2
 	elif [[ $TAIL == *"Sync process successfully completed"* ]]; then
   		STATUS="ADI INGEST SUCCESSFUL"
		echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
		echo "OK - ADI INGEST SUCCESSFUL"
		exit 0
	elif [[ $TAIL == *"Master funnel controller operational"* ]]; then
                STATUS="ADI INGEST SUCCESSFUL"
                echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
                echo "OK - ADI INGEST SUCCESSFUL"
                exit 0
 	else
  		STATUS="UNEXPECTED END OF ADI-GET RUN"
		echo STATUS=\"$(echo $STATUS)\" > /tmp/adi-status_nrpe.txt
		echo "WARNING - $STATUS"
		exit 1
 	fi
fi
