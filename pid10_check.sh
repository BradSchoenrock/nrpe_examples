#!/bin/bash

STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3
STATE_DEPENDENT=4

PROGNAME=`basename $0`

centos()
{
  version=$(egrep '7\.' /etc/redhat-release)
  if [[ ! -z $version ]]; then
        srcIP=$(ifconfig eth1 | awk '/inet\ /{print ($2)}')
  else
	srcIP=$(ifconfig eth1 | awk '/inet addr/{print substr($2,6)}')
  fi
}

## Grab Source IP from eth1 interface based on OS version
centos

#check if there is IP on eth1
if [ -z $srcIP ];then
	echo "WARNING: no IP address on eth1(standby server?)"
	exit 1
fi

##grab Multicast IP
mcastIP=$(grep udpMulticastOutput /opt/sandt/conf/tsplayer/tsplayer0/\$\$multiplex.xml|cut -d'"' -f2)
if [ -z $mcastIP ];then
        echo "WARNING: no multicast IP found in multiplex.xml"
        exit 1
fi

## Cleanup tmp files function
cleanup () 
{
  if [ -f /tmp/test.out ]; then 
    rm /tmp/test.out
  fi
  if [ -f /tmp/test.ts ]; then
    rm /tmp/test.ts
  fi
}

## Pull in multicast TS
/usr/lib64/nagios/plugins/nrpe/mcvr -m $mcastIP -p 5357 -s $srcIP -t 3 1 > /tmp/test.ts 2>/dev/null
## Parse TS for PID data
if [ -f /tmp/test.ts ] && [ -s /tmp/test.ts ]  ## /tmp/test.ts must exist and not be 0 bytes.
then
  /opt/sandt/tsbroadcaster/java/bin/java -jar /usr/lib64/nagios/plugins/nrpe/ts-monitor.jar -f /tmp/test.ts >> /tmp/test.out 
else
  echo "WARNING: something went wrong with mcvr utility"
  cleanup
  exit 1
fi

## Look for PID O in output
if [ -f /tmp/test.out ] && ( grep -qi '10 PAT' /tmp/test.out )
then
  echo "ERROR: PID-10 Found in OOB output stream!"  ## Critical status
  cleanup
  exit 2
else
  echo "OK: PID-10 not found."  ## Good status
  cleanup
  exit 0
fi

