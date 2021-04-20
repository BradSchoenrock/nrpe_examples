# This script will Monitor/ compare Aerospike database size and it will alert  on the mentioned threshold values .

USAGE="$(basename "$0") [-w|--warning] [-c|--critical]"
THRESHOLD_USAGE="WARNING threshold must be less than CRITICAL: $(basename "$0") $*"

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
# verify input
if [[ $warning -eq $critical || $warning -gt $critical ]]
then
        echo ""
        echo "$THRESHOLD_USAGE"
        echo ""
        echo "Usage: $USAGE"
        echo ""
        exit 0
fi

# Database size and file size

usage=$(du -sh /opt/aerospike/data/avn-psm.dat | cut -f1 -dG)
configSize=$(grep filesize /etc/aerospike/aerospike.conf | cut -f21 -d" " | cut -f1 -dG)

percent=`echo "scale=2; $usage/$configSize*100" | bc`


if [[ "$(echo "$percent >=  $critical"|bc)" -eq 1 ]]
        then
                echo "CRITICAL"
                exit 2
fi
if [[ "$(echo "$percent >=  $warning"|bc)" -eq 1 ]]
        then
                echo "WARNING"
                exit 1
fi
if [[ "$(echo "$percent <  $warning"|bc)" -eq 1 ]]
        then
                echo "OK"
                exit 0
fi
