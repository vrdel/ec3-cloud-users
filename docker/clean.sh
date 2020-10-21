#!/bin/bash

rm -f /var/lib/ec3-cloud-users/cache.db
rm -rf /home/hsute /home/skala /home/vpaar /shared/hsute /shared/skala /shared/vpaar
userdel hsute
userdel skala
userdel vpaar
