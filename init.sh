#!/bin/bash

echo $LD_LIBRARY_PATH

LD_LIBRARY_PATH="/db/pg9.5/run/lib/:$LD_LIBRARY_PATH"
$(export LD_LIBRARY_PATH)

echo $LD_LIBRARY_PATH
