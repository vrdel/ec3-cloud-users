#!/bin/bash

declare -a paths

paths=("$HOME/my_work/srce/git.isabella-users/isabella-users/docker/pysitepkg/sitepkg32" \
	"$HOME/my_work/srce/git.isabella-users/isabella-users/docker/pysitepkg/sitepkg64")

for f in ${paths[@]}
do
	PYTHONPATH="$PYTHONPATH:$f"
done

export PYTHONPATH
