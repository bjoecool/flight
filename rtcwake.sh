#!/bin/bash

/usr/sbin/rtcwake -m no -l -u -t $(date +%s -d 'tomorrow 6:50')
#sudo rtcwake -m no -l -u -t $(date +%s -d '21:03')
