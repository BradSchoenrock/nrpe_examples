#!/usr/bin/python

################################################################
# Script to check if the Postgres replication is running. 
# 	An interger value in the active_pid field in the pg_replication_slots table confirms the job is running fine. 
#	A NULL value shows the job is not running
# This script will be used as an NRPE plugin for ICINGA monitoring
#
# Revision History:
# 	Version: 1.0
# 	Date:    2018-08-23
################################################################

import psycopg2

try:
	conn = psycopg2.connect("dbname='icinga' user='cvo_ro' host='localhost' password='!cv0reader'")
except:
	print "CRITICAL - DB connection failed!"
	exit(2)

cur = conn.cursor()
cur.execute("""select active_pid from pg_replication_slots""")

rowcount = cur.rowcount

if rowcount == 0:
	print "CRITICAL - No Active PID for Postgres replication, Zero rows returned"
        exit(2)

rows = cur.fetchall()

for row in rows:
	active_pid=row[0]

if active_pid == "NULL":
	print "CRITICAL - Active PID for Postgres replication is NULL"
	exit(2)
else:
	print "OK - Active PID for Postgres replication is",active_pid 
	exit(0)
