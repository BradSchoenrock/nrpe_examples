#!/bin/bash

HOST=$(uname -n)
HOSTIP=`ifconfig eth0 |grep "inet " | awk '{print $2}'`
CSMHOST=`netstat -anp | grep 16668 | grep -i est | awk '{ print $5}' |grep -v e | sort -n | head -n 1| cut -d':' -f1`

#checks the number of open file descriptors on stitchers
openfiledescriptors=$(cat /proc/sys/fs/file-nr | awk '{print $1}')
Thresholdfiledescriptors=$(cat /proc/sys/fs/file-nr | awk '{print $3}')
        echo "Totalopenfiledescriptors  - is $openfiledescriptors"
        echo "Thresholdvalue for openfiledescriptors - is $Thresholdfiledescriptors"

#html5 client processes running each stitcher
        html5clientprocessesrunning=$(ps -ef | grep -i html5 | wc -l)
        echo "processesrunning-html5client -  $html5clientprocessesrunning"

#checks the number of sessions on a each stitcher
CSM_Result=`curl -s http://$CSMHOST:9099/DownstreamPlugin?cmd=status | grep -i load |grep -w $HOSTIP | awk -F "</*td>|</*tr>" '/<\/*t[rd]>.*[0-9][0-9]/ {print   $11+$13+$15}'`
    echo "Total Sessions on a stitcher - is $CSM_Result"
