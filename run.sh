#!/bin/bash

cd /db/github/flight/expedia

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/db/pg9.5/run/lib

/db/github/flight/expedia/main.py

