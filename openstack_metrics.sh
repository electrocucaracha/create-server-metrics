#! /bin/bash

DATE=`date +%Y-%m-%d`
FILE=/tmp/openstack-${DATE}.log
REPORT=/srv/http/osprofiler/metrics/openstack-${DATE}.html

echo "Clean up"

pushd /var/log/

rm ${FILE}
rm ${REPORT}
rm keystone/*.log
rm glance/*.log
rm nova/*.log

source /root/admin-openrc.sh

openstack server create report-${DATE} --image clearlinux-${DATE} --flavor 2

touch ${FILE}

grep -Rh "INFO" keystone/*.log |  cut -d ' ' -f 1,2,5 >> ${FILE}
grep -Rh "INFO" glance/*.log  |  cut -d ' ' -f 1,2,5 >> ${FILE}
grep -Rh "INFO" nova/*.log |  cut -d ' ' -f 1,2,5 >> ${FILE}

sort -o ${FILE} ${FILE}

popd

python generate_report.py -i ${FILE} -o ${REPORT}
