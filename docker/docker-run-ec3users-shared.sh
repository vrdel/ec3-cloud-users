#!/bin/bash

if [ -z "$1" ]
then
	IMG="ipanema:5000/ec3-cloud-users"
else
	IMG="ipanema:5000/ec3-cloud-users:$1"
fi

docker rm ec3-cloud-users; \
docker run --privileged --rm -ti \
-h isabella \
-e ZDOTDIR="/mnt" \
--log-driver json-file --log-opt max-size=10m \
-v /dev/log:/dev/log \
-v /etc/localtime:/etc/localtime:ro \
-v $HOME:/mnt \
-v /home/daniel/my_work/srce/git.isabella-users/docker/pysitepkg:/root/pysitepkg \
-v /home/daniel/my_work/srce/git.isabella-users/docker/syncsite.sh:/root/syncsite.sh \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/:/root/isabella-users \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/config_values/:/etc/isabella-users-frontend:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/modules/:/usr/lib/python2.6/site-packages/isabella_users_frontend:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/puppet/modules/:/usr/lib/python2.6/site-packages/isabella_users_puppet:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/puppet/config_values/:/etc/isabella-users-puppet:ro \
-v /home/daniel/my_work/srce/git.isabella-users/KeyBot/:/root/KeyBot \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/puppet/bin/sync-feeddb.py:/usr/libexec/isabella-users-puppet/sync-feeddb.py:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/puppet/bin/setup-db.py:/usr/libexec/isabella-users-puppet/setup-db.py:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/puppet/bin/update-userdb.py:/usr/libexec/isabella-users-puppet/update-userdb.py:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/puppet/bin/update-useryaml.py:/usr/libexec/isabella-users-puppet/update-useryaml.py:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/bin/create-accounts.py:/usr/libexec/isabella-users-frontend/create-accounts.py:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/bin/setup-db.py:/usr/libexec/isabella-users-frontend/setup-db.py:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/bin/update-userdb.py:/usr/libexec/isabella-users-frontend/update-userdb.py:ro \
--name ec3-cloud-users \
$IMG /bin/zsh
