#!/usr/bin/env python
import argparse, requests, socket, sys
from bs4 import BeautifulSoup

# Nagios error codes:
OK=0
WARN=1
CRIT=2
UNKNOWN=3
DEPENDENT=4

# Parse arguments
parser = argparse.ArgumentParser(description='Check for Multiple Topologies from CSM DownstreamPlugin page.', usage='%(prog)s [options]')

parser.add_argument('-w', '--warning', type=int, default=2,
                    help='Threshold to throw WARNING return code (default: 2)')
parser.add_argument('-c', '--critical', type=int, default=3,
                    help='Threshold to throw CRITICAL return code (default: 3)')
parser.add_argument('-u', '--url',
                    default="http://" + socket.getfqdn() + ":9099" + "/DownstreamPlugin?cmd=status",
                    help='URL, (including port) to CSM downstream plugin status page. default: http://LOCAL_FQDN:9099/DownstreamPlugin?cmd=status')
args = parser.parse_args()

# Set args to variables
warningThreshold = args.warning
criticalThreshold = args.critical
targetURL = args.url

# Seed variables
topology_count = 1
topology = "empty"

# Define and snatch target URL contents
try:
  page = requests.get(targetURL)
except requests.exceptions.RequestException as err:
  print(err)
  sys.exit(UNKNOWN)

# Store the page html in the soup var
soup = BeautifulSoup(page.text, 'html.parser')

# Get me all the tables on the page
tables = soup("table")

# Iterate through the tables, looking for a row containing a table header with the string I want
for table in tables:
  if table.find("tr").find("th", text="Service Area ID"):
    # Set seed vars for later
    for row in table:
        # Split out empty rows and the header row
        if row == "\n" or row.find("th"):
          continue
        else:
          # This finds the _first_ "td" tag in the row
          for service_area_and_topology in row.find("td"):

            # Die if unreadable data
            if ":" not in service_area_and_topology:
              print "UNKNOWN :", service_area_and_topology
              sys.exit(UNKNOWN)

            # First iteration, set var to first value
            if topology == "empty":
              topology = service_area_and_topology.split(":")[1]

            # The rest of the iterations, checking against that first value
            elif service_area_and_topology.split(":")[1] == topology:
              continue
            else:
              topology_count += 1

# Tally it up and check against thresholds
if topology_count >= criticalThreshold:
  print "CRITICAL - Topology Count:", topology_count
  sys.exit(CRIT)
elif topology_count >= warningThreshold:
  print "WARNING - Topology Count:", topology_count
  sys.exit(WARN)
else:
  # We made it!
  print "OK - Topology Count:", topology_count
  sys.exit(OK)
