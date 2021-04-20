#!/bin/bash

HOST=$(uname -n)

CURLRESULT=$(curl -s http://$HOST:9099/cluster?cmd=checkRunning) 
CURLRESULT=$(echo $CURLRESULT | sed 's/<html><body>//g')
CURLRESULT=$(echo $CURLRESULT | sed 's/<\/body><\/html>//g')

if [ $CURLRESULT == "HEALTHY" ]
then
	echo "OK - Cluster state is HEALTHY"
	exit 0
elif [ $CURLRESULT == "waiting" ]
then
	echo "CRITICAL - Cluster state is waiting"
	exit 2
else
	echo "WARNING - Cluster state is $CURLRESULT"
	exit 1
fi
