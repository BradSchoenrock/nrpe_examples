#!/usr/bin/python
######################################################################
#check_wb_hhsyn                                                      #
#                                                                    # 
#Purpose:                                                            #
#Run WB synthetic transactions for VEMM counts against dummy test WB #
#If unexpected results, warn to Icinga. Errors reported to NOC       #
#                                                                    #
#Usage:                                                              #
#Check to be run via NRPE with no flags                              #
#                                                                    #
#NOTES:                                                              #
######################################################################
#  Rev  #  Edit by:     # Change                          # Date     #
######################################################################
#  1.0  # CK - VO PE    #  Initial release                # 01/15/16 #
######################################################################

import urllib2, urllib
import sys, re

## Update offers on dummy WB household
def modOffers( adddel ):
  boaURLcgi = "http://www01lttnco.lttn.co.charter.com/BOA/cgi-bin/boa_send.cgi"
  header = {'Content-Type': 'application/text'}

  hh = 'VO_monitoring'
  if adddel=="add":
    pkg = 'VOD_CTE'
  elif adddel=="del":
    pkg = ''
  else:
    #print "Matched nothing!\n"
    sys.exit(1)
      
  data = urllib.urlencode({'dest': 'boa.g.charter.com:8080', 'hit_type': 'index.php?hit_type=modifyHouseholdAuthorizations', 'household': hh, 'auths': pkg})

  boaRequest = urllib2.Request(boaURLcgi, data)
  #boaRequest.add_header(header)
  response = urllib2.urlopen(boaRequest)
  boaResponse = response.read()
  response.close()

  #print "Response: " + boaResponse
    
  if re.search("No-Error", boaResponse) is not None:
    #print "No error\n"    ## DEBUG ONLY
    return 0
  else:
    #print "Fail!\n"    ## DEBUG ONLY
    return 100



    
## Get count of VEMMs for test dummy WB
## function pulled from stb_sum.py provided by:
## 'STB emulation utility (c) by cisco 2016 ygilbaum@cisco.com. Ver. 0.00.01'
def getVEMMcount():
  #sgw_host = "172.28.129.201:8010"
  sgw_host = "localhost:8010"
  deviceid = "000000000000000000000001"

  #url = "http://" + sgw_host + "/unilateral?NdsTargetURL=I30"
  url = "http://" + sgw_host + "/unilateral?NdsTargetURL=VGSServer_AllVemmsRequest"
  data = "0530" + deviceid + "0451b7b3ac0015"

  req = urllib2.Request(url, data, {'Content-Type': 'application/text'})
  try:
    f = urllib2.urlopen(req)

    blb = ""
    for x in f:
      blb = blb + x
    f.close()

    res = 0
    contp = 0
    if blb.find('A91B', 0) != -1:
      while res != -1:
        res = blb.find('A91B', res + 1)
        contp = contp + 1
      contp = contp - 1

    res = 0
    cont = 0;
    if blb.find('A90B', 0) != -1:
      while res != -1:
        res = blb.find('A90B', res + 1)
        cont = cont + 1
      cont = cont - 1

    if (cont + contp) == 0:
      #print "Device " + deviceid + " a). Is not found in db or b). Wasn't connected to HH or c). Is not registred"
      return 100
    else:
      #print 'Positive VEMMS: ' + str(contp) + ' of total ' + str(cont + contp)
      return contp

  except:
    #print 'Error. Please check DeviceID format'
    return 100

## ALl good exit
def ok():
	print 'HH provisioning test process sucessfully!'
  sys.exit(0)

## Something wonky happened, needs investigating but not NOC escalated
def warn():
  print 'HH provisioning test process ended early, investigation required!'
  sys.exit(1)
  
## Something failed, Critial to NOC alarm
def critical():
  print 'HH provisioning test process failed!'
  sys.exit(2)

    
## MAIN function
def main():
  rtn = 1
  ## Call getVEMMs, count should = 1
  rtn = getVEMMcount()
  #print "rtn after getVEMMcount #1 = " + str(rtn)    ## DEBUG ONLY
  if(rtn == 100):
    warn()    ## something wonky happened
  elif(rtn == 2): 
    critical()    ## check failed, exit critical
  ## Call modOffers(add)
  rtn = modOffers("add")
  #print "rtn after modOffers(add) = " +  str(rtn)    ## DEBUG ONLY
  if(rtn == 100):
    warn()    ## something wonky happened
  ## Call getVEMMs, count should = 2
  rtn = getVEMMcount()
  #print "rtn after getVEMMcount #1 = " +  str(rtn)   ## DEBUG ONLY
  if(rtn != 2):
    if(rtn == 100):
      warn()    ## something wonky happened
    else:
      critical()    ## check failed, exit critical
  ## call modOffers(del)
  rtn = modOffers("del")
  #print "rtn after modOffers(del) = " +  str(rtn)    ## DEBUG ONLY
  if(rtn == 100):
    warn()    ## something wonky happened
  ## Call getVEMMs, count should = 1
  rtn = getVEMMcount()
  #print "rtn after getVEMMcount #3 = " +  str(rtn)   ## DEBUG ONLY
  if(rtn != 1):
    if(rtn == 100):
      warn()    ## something wonky happened
    else:
      critical()    ## check failed, exit critical
  ## Nothing failed return OK status
  ok()  
        
## Start the magic
if __name__ == "__main__":
    main()
