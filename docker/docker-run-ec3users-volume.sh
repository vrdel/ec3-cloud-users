#!/bin/bash

docker rm ec3-cloud-users; \
docker run --privileged --rm -ti \
-e ZDOTDIR="/mnt" \
--log-driver json-file --log-opt max-size=10m \
-v /dev/log:/dev/log \
-v /etc/localtime:/etc/localtime:ro \
-v $HOME:/mnt \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/:/root/isabella-users \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/modules/:/usr/lib/python2.6/site-packages/isabella_users_frontend:ro \
-v /home/daniel/my_work/srce/git.isabella-users/isabella-users/frontend/config_values/:/etc/isabella-users-frontend:ro \
-v /home/daniel/my_work/srce/git.isabella-users/KeyBot/:/root/KeyBot \
--name ec3-cloud-users \
ipanema:5000/ec3-cloud-users-volume /bin/zsh
