#!/bin/bash
res=2

test=$((curl -vk -F xmlfile=@/usr/lib64/nagios/plugins/nrpe/dcas_clearoffer.xml http://localhost:5155/CatalogImport/uploadXti) 2>&1)

if [[ "$test" =~ "HTTP/1.1 200 OK" ]]
  then res=0; echo "Check passed!";
else
  echo "Unable to process clear offer, investigation required.";
fi

exit $res
