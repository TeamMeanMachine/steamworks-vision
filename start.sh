#!/bin/bash

SCRIPTPATH=$(dirname $0)
modprobe uvcvideo

while true
do
    python3 $SCRIPTPATH/main.py
    echo "Restarting..."
    sleep 1
done
