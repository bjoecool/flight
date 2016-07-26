#!/bin/bash

sudo rtcwake -m no -l -u -t $(date +%s -d 'tomorrow 7:00')
#sudo rtcwake -m no -l -u -t $(date +%s -d '21:03')
