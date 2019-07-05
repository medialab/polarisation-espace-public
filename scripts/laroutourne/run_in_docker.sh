#!/bin/bash

cd $(dirname $0)
curpath=$(pwd)

docker pull tiagopeixoto/graph-tool

docker run -it -u user -w /home/user/laroutourne --mount "type=bind,source=$curpath,target=/home/user/laroutourne" tiagopeixoto/graph-tool python laroutourne.py "$1"

