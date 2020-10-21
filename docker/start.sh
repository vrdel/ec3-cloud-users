#!/bin/bash

rm -f /var/lib/ec3-cloud-users/cache.db
sqlite3 /var/lib/ec3-cloud-users/cache.db < /root/ec3-cloud-users/helpers/dbcreate.sql
useradd -M hsute -g 100
useradd -M vpaar -g 100
useradd -M skala -g 100
