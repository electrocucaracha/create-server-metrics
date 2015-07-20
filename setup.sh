#! /bin/bash

REPORT_DIR=/srv/http/performance/
HOSTNAME=`hostname`

mkdir -p /etc/httpd/conf.d
cat <<EOL > /etc/httpd/conf.d/performance.conf
Listen 8080

<VirtualHost *:8080>
 ServerName ${HOSTNAME}
  DocumentRoot ${REPORT_DIR}

    <Directory ${REPORT_DIR}>
        Options FollowSymLinks MultiViews Indexes
        AllowOverride None
        Require all granted
    </Directory>

</VirtualHost>
EOL

systemctl restart httpd
