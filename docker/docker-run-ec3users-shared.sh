#!/bin/bash

if [ -z "$1" ]
then
	IMG="ipanema:5000/ec3-cloud-users"
else
	IMG="ipanema:5000/ec3-cloud-users:$1"
fi

docker rm ec3-cloud-users; \
docker run --privileged --rm -ti \
-h ec3-cloud-users \
-e ZDOTDIR="/mnt" \
--log-driver json-file --log-opt max-size=10m \
-v /dev/log:/dev/log \
-v /etc/localtime:/etc/localtime:ro \
-v $HOME:/mnt \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/docker/pysitepkg:/home/user/pysitepkg \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/docker/syncsite.sh:/home/user/syncsite.sh \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/:/home/user/ec3-cloud-users \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/config_values/:/etc/ec3-cloud-users:ro \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/modules/:/usr/lib/python2.7/site-packages/ec3_cloud_users:ro \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/bin/create-accounts.py:/usr/libexec/ec3-cloud-users/create-accounts.py:ro \
-v $HOME/my_work/srce/git.ec3-cloud-users/ec3-cloud-users/bin/sync-feed.py:/usr/libexec/ec3-cloud-users/sync-feed.py:ro \
--name ec3-cloud-users \
$IMG /bin/zsh
