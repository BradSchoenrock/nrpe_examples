#!/bin/bash

if [ -s "/opt/sandt/conf/tsplayer/tsplayer0/\$\$multiplex.xml" ] && [ -s "/opt/sandt/conf/tsplayer/tsplayer1/\$\$multiplex.xml" ] && [ -s "/opt/sandt/conf/tsplayer/tsplayer2/\$\$multiplex.xml" ] && [ -s "/opt/sandt/conf/tsplayer/tsplayer3/\$\$multiplex.xml" ]; then
        echo "OK - multiplex.xml Files exists on tsplayers0-3 and all are non zero size"
	exit 0
else
        echo "CRITICAL - multiplex.xml File doesnt exist on one or more tsplayers0-3 or in zero size"
	exit 2
fi
