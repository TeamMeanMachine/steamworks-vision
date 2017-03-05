#!/bin/bash

SCRIPTPATH=$(dirname $0)

while true
do
    python $SCRIPTPATH/main.py debug boiler network
    echo "Restarting..."
    sleep 1
done
