#!/bin/bash
# Using Graph tool's docker installation https://git.skewed.de/count0/graph-tool/wikis/installation-instructions#installing-using-docker

# call with : bash run_in_docker.sh <GRAPHML_FILE> [<WHEEL_IMG_WIDTH>]

cd $(dirname $0)
curpath=$(pwd)

GRAPHML_FILE=$1
NB_STEPS=$2
IMG_WIDTH=$3

docker pull tiagopeixoto/graph-tool > /tmp/pull-docker-graph-tool.log 2>&1 || (cat /tmp/pull-docker-graph-tool.log && exit)

time docker run -it -u user -w /home/user/laroutourne --mount "type=bind,source=$curpath,target=/home/user/laroutourne" tiagopeixoto/graph-tool python laroutourne.py "$GRAPHML_FILE" "$NB_STEPS"

time docker run -it -u user -w /home/user/laroutourne --mount "type=bind,source=$curpath,target=/home/user/laroutourne" tiagopeixoto/graph-tool python draw_wheel.py "$GRAPHML_FILE" $IMG_WIDTH
