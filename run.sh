#!/bin/bash

cd /db/github/flight
./test.py
. ./init.sh
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/db/pg9.5/run/lib
export 
./main.py
echo 'main.py'>b.txt
