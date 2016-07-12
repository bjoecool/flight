#!/bin/bash

sudo rtcwake -m no -l -u -t $(date +%s -d 'tomorrow 16:30')
