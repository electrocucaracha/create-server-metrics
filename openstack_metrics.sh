#! /bin/bash

DATE=`date +%Y-%m-%d`
FILE=/tmp/openstack-${DATE}.log
REPORT=/srv/http/performance/openstack-${DATE}.html

echo "Clean up"

pushd /var/log/

rm -rf ${FILE}
rm -rf ${REPORT}
rm -rf keystone/*.log
rm -rf glance/*.log
rm -rf nova/*.log

source /root/admin-openrc.sh

openstack server create report-${DATE} --image clearlinux-${DATE} --flavor 2 --wait

touch ${FILE}

grep -Rh "ERROR\|WARN\|INFO\|DEBUG\|TRACE" keystone/*.log |  cut -d ' ' -f 1,2,5 >> ${FILE}
grep -Rh "ERROR\|WARN\|INFO\|DEBUG\|TRACE" glance/*.log  |  cut -d ' ' -f 1,2,5 >> ${FILE}
grep -Rh "ERROR\|WARN\|INFO\|DEBUG\|TRACE" nova/*.log |  cut -d ' ' -f 1,2,5 >> ${FILE}

sort -o ${FILE} ${FILE}

popd

python generate_report.py -i ${FILE} -o ${REPORT}
