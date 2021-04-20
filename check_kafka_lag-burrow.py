#!/usr/bin/python

import os,json,sys
cmd = "curl -s localhost:8000/v3/kafka/local/consumer/%s/status > /tmp/results.json" %sys.argv[1]
if os.system(cmd) != 0:
	print "Burrow curl failed"
	exit(2)
json_file = open("/tmp/results.json", "r")
json_payload = json.load(json_file)
if json_payload["status"]["status"] == "OK":
	print "Lag status is %s and totallag is %s" %(json_payload["status"]["status"], json_payload["status"]["totallag"])
	exit(0)
else:
	print "Lag status is %s and totallag is %s" %(json_payload["status"]["status"], json_payload["status"]["totallag"])
	exit(2)
