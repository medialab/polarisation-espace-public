#!/bin/bash
# Using Graph tool's docker installation https://git.skewed.de/count0/graph-tool/wikis/installation-instructions#installing-using-docker

# call with : bash run_in_docker.sh <INPUT_FILE (.graphml or .state)> [<NB_ATTEMPTS>] [<MAX_CLUSTERS>] [<WHEEL_IMG_WIDTH>]

cd $(dirname $0)
curpath=$(pwd)

INPUT_FILE=$1
NB_ATTEMPTS=$2
MAX_CLUSTERS=$3
IMG_WIDTH=$4

docker pull tiagopeixoto/graph-tool > /tmp/pull-docker-graph-tool.log 2>&1 || (cat /tmp/pull-docker-graph-tool.log && exit)

if echo $INPUT_FILE | grep .graphml > /dev/null; then
  time docker run -it -u user -w /home/user/laroutourne --mount "type=bind,source=$curpath,target=/home/user/laroutourne" tiagopeixoto/graph-tool python laroutourne.py "$INPUT_FILE" $NB_ATTEMPTS $MAX_CLUSTERS $IMG_WIDTH
elif echo $INPUT_FILE | grep .state > /dev/null; then
  time docker run -it -u user -w /home/user/laroutourne --mount "type=bind,source=$curpath,target=/home/user/laroutourne" tiagopeixoto/graph-tool python draw_wheel.py "$INPUT_FILE" $NB_ATTEMPTS
fi
